-- Application-owned schema only. Never create or modify managed auth internals.
REVOKE ALL ON SCHEMA app FROM PUBLIC, anon, authenticated;
GRANT USAGE ON SCHEMA app TO spendwise_runtime;
ALTER DEFAULT PRIVILEGES IN SCHEMA app REVOKE EXECUTE ON FUNCTIONS FROM PUBLIC;

CREATE TABLE app.profiles (
    id uuid PRIMARY KEY REFERENCES auth.users(id) ON DELETE RESTRICT,
    display_name text NOT NULL CHECK (display_name = btrim(display_name) AND length(display_name) BETWEEN 1 AND 100),
    created_at timestamptz NOT NULL DEFAULT now(),
    updated_at timestamptz NOT NULL DEFAULT now()
);
CREATE TABLE app.groups (
    id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
    name text NOT NULL CHECK (name = btrim(name) AND length(name) BETWEEN 1 AND 100),
    currency_code text NOT NULL CHECK (currency_code IN ('INR','USD','CAD','GBP','EUR')),
    timezone text NOT NULL,
    currency_locked_at timestamptz,
    is_active boolean NOT NULL DEFAULT true,
    created_by uuid NOT NULL REFERENCES app.profiles(id),
    created_at timestamptz NOT NULL DEFAULT now(),
    updated_at timestamptz NOT NULL DEFAULT now()
);
CREATE TABLE app.group_memberships (
    id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
    group_id uuid NOT NULL REFERENCES app.groups(id),
    profile_id uuid NOT NULL REFERENCES app.profiles(id),
    is_active boolean NOT NULL DEFAULT true,
    first_joined_at timestamptz NOT NULL DEFAULT now(),
    last_joined_at timestamptz NOT NULL DEFAULT now(),
    departed_at timestamptz,
    UNIQUE (group_id, profile_id), UNIQUE (group_id, id),
    CHECK (is_active = (departed_at IS NULL))
);
CREATE INDEX memberships_active ON app.group_memberships(profile_id,group_id) WHERE is_active;
CREATE TABLE app.group_invitations (
    id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
    group_id uuid NOT NULL REFERENCES app.groups(id),
    token_hash bytea NOT NULL UNIQUE CHECK (octet_length(token_hash)=32),
    created_by uuid NOT NULL REFERENCES app.profiles(id),
    created_at timestamptz NOT NULL DEFAULT now(),
    expires_at timestamptz NOT NULL DEFAULT now() + interval '7 days',
    revoked_at timestamptz,
    revoked_by uuid REFERENCES app.profiles(id),
    UNIQUE (group_id,id), CHECK (expires_at > created_at),
    CHECK ((revoked_at IS NULL) = (revoked_by IS NULL))
);
CREATE INDEX invitations_issuer ON app.group_invitations(group_id,created_by) WHERE revoked_at IS NULL;
CREATE TABLE app.membership_events (
    id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
    group_id uuid NOT NULL REFERENCES app.groups(id),
    membership_id uuid NOT NULL,
    event_type text NOT NULL CHECK (event_type IN ('joined','left','removed')),
    actor_id uuid NOT NULL REFERENCES app.profiles(id),
    invitation_id uuid,
    occurred_at timestamptz NOT NULL DEFAULT now(),
    FOREIGN KEY (group_id,membership_id) REFERENCES app.group_memberships(group_id,id),
    FOREIGN KEY (group_id,invitation_id) REFERENCES app.group_invitations(group_id,id)
);
CREATE INDEX membership_events_order ON app.membership_events(membership_id,occurred_at,id);
CREATE TABLE app.expenses (
    id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
    group_id uuid NOT NULL REFERENCES app.groups(id),
    payer_membership_id uuid NOT NULL,
    name text NOT NULL CHECK (name=btrim(name) AND length(name) BETWEEN 1 AND 200),
    amount_minor bigint NOT NULL CHECK (amount_minor BETWEEN 1 AND 99999999999),
    transaction_date date NOT NULL,
    split_method text NOT NULL CHECK (split_method IN ('equal','exact','percentage')),
    version integer NOT NULL DEFAULT 1 CHECK (version>0),
    created_by uuid NOT NULL REFERENCES app.profiles(id),
    updated_by uuid NOT NULL REFERENCES app.profiles(id),
    created_at timestamptz NOT NULL DEFAULT now(),
    updated_at timestamptz NOT NULL DEFAULT now(),
    deleted_at timestamptz,
    UNIQUE (group_id,id),
    FOREIGN KEY (group_id,payer_membership_id) REFERENCES app.group_memberships(group_id,id)
);
CREATE INDEX expenses_order ON app.expenses(group_id,transaction_date DESC,created_at DESC,id DESC) WHERE deleted_at IS NULL;
CREATE INDEX expenses_payer ON app.expenses(group_id,payer_membership_id);
CREATE TABLE app.expense_shares (
    expense_id uuid NOT NULL,
    membership_id uuid NOT NULL,
    group_id uuid NOT NULL REFERENCES app.groups(id),
    amount_minor bigint NOT NULL CHECK (amount_minor BETWEEN 0 AND 99999999999),
    percentage_basis_points integer CHECK (percentage_basis_points BETWEEN 0 AND 10000),
    PRIMARY KEY (expense_id,membership_id),
    FOREIGN KEY (group_id,expense_id) REFERENCES app.expenses(group_id,id),
    FOREIGN KEY (group_id,membership_id) REFERENCES app.group_memberships(group_id,id)
);
CREATE INDEX shares_member ON app.expense_shares(group_id,membership_id,expense_id);
CREATE TABLE app.repayments (
    id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
    group_id uuid NOT NULL REFERENCES app.groups(id),
    sender_membership_id uuid NOT NULL,
    recipient_membership_id uuid NOT NULL,
    amount_minor bigint NOT NULL CHECK (amount_minor BETWEEN 1 AND 99999999999),
    transaction_date date NOT NULL,
    payment_method text NOT NULL DEFAULT 'cash' CHECK (payment_method IN ('cash','other')),
    payment_method_label text,
    version integer NOT NULL DEFAULT 1 CHECK (version>0),
    created_by uuid NOT NULL REFERENCES app.profiles(id),
    updated_by uuid NOT NULL REFERENCES app.profiles(id),
    created_at timestamptz NOT NULL DEFAULT now(),
    updated_at timestamptz NOT NULL DEFAULT now(),
    deleted_at timestamptz,
    UNIQUE (group_id,id),
    FOREIGN KEY (group_id,sender_membership_id) REFERENCES app.group_memberships(group_id,id),
    FOREIGN KEY (group_id,recipient_membership_id) REFERENCES app.group_memberships(group_id,id),
    CHECK (sender_membership_id <> recipient_membership_id),
    CHECK ((payment_method='cash' AND payment_method_label IS NULL) OR
        (payment_method='other' AND payment_method_label IS NOT NULL AND
         payment_method_label=btrim(payment_method_label) AND length(payment_method_label) BETWEEN 1 AND 100))
);
CREATE INDEX repayments_order ON app.repayments(group_id,transaction_date DESC,created_at DESC,id DESC) WHERE deleted_at IS NULL;
CREATE INDEX repayments_sender ON app.repayments(group_id,sender_membership_id);
CREATE INDEX repayments_recipient ON app.repayments(group_id,recipient_membership_id);

CREATE TABLE app.expense_revisions (
    id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
    group_id uuid NOT NULL REFERENCES app.groups(id),
    expense_id uuid NOT NULL,
    version integer NOT NULL CHECK (version>0),
    action text NOT NULL CHECK (action IN ('created','updated','deleted')),
    actor_id uuid NOT NULL REFERENCES app.profiles(id),
    occurred_at timestamptz NOT NULL DEFAULT now(),
    before_values jsonb,
    after_values jsonb NOT NULL CHECK (jsonb_typeof(after_values)='object'),
    UNIQUE (expense_id,version),
    FOREIGN KEY (group_id,expense_id) REFERENCES app.expenses(group_id,id),
    CHECK ((action='created' AND before_values IS NULL AND version=1) OR
        (action<>'created' AND before_values IS NOT NULL AND jsonb_typeof(before_values)='object' AND version>1))
);
CREATE INDEX expense_revisions_order ON app.expense_revisions(group_id,occurred_at,id);
CREATE TABLE app.repayment_revisions (
    id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
    group_id uuid NOT NULL REFERENCES app.groups(id),
    repayment_id uuid NOT NULL,
    version integer NOT NULL CHECK (version>0),
    action text NOT NULL CHECK (action IN ('created','updated','deleted')),
    actor_id uuid NOT NULL REFERENCES app.profiles(id),
    occurred_at timestamptz NOT NULL DEFAULT now(),
    before_values jsonb,
    after_values jsonb NOT NULL CHECK (jsonb_typeof(after_values)='object'),
    UNIQUE (repayment_id,version),
    FOREIGN KEY (group_id,repayment_id) REFERENCES app.repayments(group_id,id),
    CHECK ((action='created' AND before_values IS NULL AND version=1) OR
        (action<>'created' AND before_values IS NOT NULL AND jsonb_typeof(before_values)='object' AND version>1))
);
CREATE INDEX repayment_revisions_order ON app.repayment_revisions(group_id,occurred_at,id);
CREATE TABLE app.idempotency_requests (
    actor_id uuid NOT NULL REFERENCES app.profiles(id),
    request_key uuid NOT NULL,
    group_id uuid NOT NULL REFERENCES app.groups(id),
    operation text NOT NULL CHECK (operation IN (
        'create_expense','replace_expense','delete_expense',
        'create_repayment','replace_repayment','delete_repayment')),
    request_hash bytea NOT NULL CHECK (octet_length(request_hash)=32),
    response_status smallint NOT NULL CHECK (response_status IN (200,201)),
    response_body jsonb NOT NULL CHECK (jsonb_typeof(response_body)='object'),
    created_at timestamptz NOT NULL DEFAULT now(),
    PRIMARY KEY(actor_id,request_key)
);
CREATE INDEX idempotency_group ON app.idempotency_requests(group_id);

CREATE FUNCTION app.reject_mutation() RETURNS trigger LANGUAGE plpgsql AS $$
BEGIN
    RAISE EXCEPTION 'Immutable record' USING ERRCODE='23514';
END $$;
CREATE TRIGGER membership_events_immutable BEFORE UPDATE OR DELETE ON app.membership_events FOR EACH ROW EXECUTE FUNCTION app.reject_mutation();
CREATE TRIGGER expense_revisions_immutable BEFORE UPDATE OR DELETE ON app.expense_revisions FOR EACH ROW EXECUTE FUNCTION app.reject_mutation();
CREATE TRIGGER repayment_revisions_immutable BEFORE UPDATE OR DELETE ON app.repayment_revisions FOR EACH ROW EXECUTE FUNCTION app.reject_mutation();
CREATE TRIGGER retry_results_immutable BEFORE UPDATE OR DELETE ON app.idempotency_requests FOR EACH ROW EXECUTE FUNCTION app.reject_mutation();
CREATE TRIGGER memberships_preserved BEFORE DELETE ON app.group_memberships FOR EACH ROW EXECUTE FUNCTION app.reject_mutation();
CREATE TRIGGER expenses_preserved BEFORE DELETE ON app.expenses FOR EACH ROW EXECUTE FUNCTION app.reject_mutation();
CREATE TRIGGER repayments_preserved BEFORE DELETE ON app.repayments FOR EACH ROW EXECUTE FUNCTION app.reject_mutation();

CREATE FUNCTION app.validate_group() RETURNS trigger LANGUAGE plpgsql AS $$
BEGIN
    IF NOT EXISTS(SELECT 1 FROM pg_timezone_names WHERE name=NEW.timezone) THEN
        RAISE EXCEPTION 'Invalid timezone' USING ERRCODE='23514';
    END IF;
    IF TG_OP='UPDATE' THEN
        IF NEW.timezone IS DISTINCT FROM OLD.timezone OR
           (OLD.currency_locked_at IS NOT NULL AND
             (NEW.currency_locked_at IS DISTINCT FROM OLD.currency_locked_at OR
              NEW.currency_code IS DISTINCT FROM OLD.currency_code)) THEN
            RAISE EXCEPTION 'Immutable group settings' USING ERRCODE='23514';
        END IF;
    END IF;
    RETURN NEW;
END $$;
CREATE TRIGGER group_settings BEFORE INSERT OR UPDATE ON app.groups FOR EACH ROW EXECUTE FUNCTION app.validate_group();
CREATE FUNCTION app.lock_currency() RETURNS trigger LANGUAGE plpgsql AS $$
BEGIN
    UPDATE app.groups SET currency_locked_at=COALESCE(currency_locked_at,now()) WHERE id=NEW.group_id;
    RETURN NEW;
END $$;
CREATE TRIGGER expense_currency AFTER INSERT ON app.expenses FOR EACH ROW EXECUTE FUNCTION app.lock_currency();
CREATE TRIGGER repayment_currency AFTER INSERT ON app.repayments FOR EACH ROW EXECUTE FUNCTION app.lock_currency();

CREATE FUNCTION app.check_expense_shares() RETURNS trigger LANGUAGE plpgsql AS $$
DECLARE
    expense_uuid uuid;
    parent app.expenses%ROWTYPE;
    count_shares bigint;
    total numeric;
    percentages bigint;
    percentage_count bigint;
BEGIN
    IF TG_TABLE_NAME='expenses' THEN
        expense_uuid := NEW.id;
    ELSE
        IF TG_OP='UPDATE' AND (NEW.expense_id IS DISTINCT FROM OLD.expense_id OR NEW.group_id IS DISTINCT FROM OLD.group_id OR NEW.membership_id IS DISTINCT FROM OLD.membership_id) THEN
            RAISE EXCEPTION 'Replace shares instead of moving them' USING ERRCODE='23514';
        END IF;
        IF TG_OP='DELETE' THEN expense_uuid := OLD.expense_id;
        ELSE expense_uuid := NEW.expense_id; END IF;
    END IF;
    SELECT * INTO parent FROM app.expenses WHERE id=expense_uuid;
    SELECT count(*),sum(amount_minor),sum(percentage_basis_points),count(percentage_basis_points)
      INTO count_shares,total,percentages,percentage_count
      FROM app.expense_shares WHERE expense_id=expense_uuid;
    IF count_shares=0 OR total IS DISTINCT FROM parent.amount_minor::numeric OR
       (parent.split_method='percentage' AND (percentages<>10000 OR percentage_count<>count_shares)) OR
       (parent.split_method<>'percentage' AND percentage_count<>0) THEN
        RAISE EXCEPTION 'Expense shares inconsistent' USING ERRCODE='23514';
    END IF;
    RETURN NULL;
END $$;
CREATE CONSTRAINT TRIGGER expense_total AFTER INSERT OR UPDATE ON app.expenses DEFERRABLE INITIALLY DEFERRED FOR EACH ROW EXECUTE FUNCTION app.check_expense_shares();
CREATE CONSTRAINT TRIGGER share_total AFTER INSERT OR UPDATE OR DELETE ON app.expense_shares DEFERRABLE INITIALLY DEFERRED FOR EACH ROW EXECUTE FUNCTION app.check_expense_shares();

REVOKE ALL ON ALL TABLES IN SCHEMA app FROM PUBLIC, anon, authenticated;
REVOKE ALL ON ALL FUNCTIONS IN SCHEMA app FROM PUBLIC, anon, authenticated;
GRANT SELECT ON ALL TABLES IN SCHEMA app TO spendwise_runtime;
GRANT INSERT, UPDATE ON app.profiles, app.groups, app.group_memberships, app.group_invitations, app.expenses, app.repayments TO spendwise_runtime;
GRANT INSERT, UPDATE, DELETE ON app.expense_shares TO spendwise_runtime;
GRANT INSERT ON app.membership_events, app.expense_revisions, app.repayment_revisions, app.idempotency_requests TO spendwise_runtime;
GRANT EXECUTE ON ALL FUNCTIONS IN SCHEMA app TO spendwise_runtime;
