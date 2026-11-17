$ErrorActionPreference = 'Stop'
Push-Location (Join-Path $PSScriptRoot '..')
try {
    if (-not (Test-Path -LiteralPath '.env.test')) {
        $fixturePassword = [guid]::NewGuid().ToString('N')
        $ownerPassword = [guid]::NewGuid().ToString('N')
        $runtimePassword = [guid]::NewGuid().ToString('N')
        @(
            "SPENDWISE_TEST_POSTGRES_PASSWORD=$fixturePassword"
            "SPENDWISE_TEST_ADMIN_URL=postgresql+psycopg://spendwise_fixture:${fixturePassword}@127.0.0.1:55432/spendwise_test"
            "SPENDWISE_TEST_MIGRATION_URL=postgresql+psycopg://spendwise_owner:${ownerPassword}@127.0.0.1:55432/spendwise_test"
            "SPENDWISE_TEST_RUNTIME_URL=postgresql+psycopg://spendwise_runtime:${runtimePassword}@127.0.0.1:55432/spendwise_test"
        ) | Set-Content -LiteralPath '.env.test' -Encoding ASCII
    }
    docker compose --env-file .env.test -f compose.test.yaml up -d --wait
    if ($LASTEXITCODE -ne 0) { throw 'Test database startup failed.' }
} finally {
    Pop-Location
}
