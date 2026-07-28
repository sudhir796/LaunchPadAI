$postResult = curl.exe -s -X POST "http://localhost:8000/ideas/" -H "Content-Type: application/json" -d "@test_payload.json"
$ideaId = ($postResult | ConvertFrom-Json).id
Write-Output "Created Idea ID: $ideaId"
Write-Output "Listening to SSE stream..."
curl.exe -N -s "http://localhost:8000/ideas/$ideaId/stream"
