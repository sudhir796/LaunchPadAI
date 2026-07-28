$postResult = curl.exe -s -X POST "http://localhost:8000/ideas/" -H "Content-Type: application/json" -d "@test_payload.json"
Write-Output "--- POST /ideas output ---"
Write-Output $postResult

$ideaId = ($postResult | ConvertFrom-Json).id

Write-Output ""
Write-Output "--- GET /ideas output ---"
curl.exe -s -X GET "http://localhost:8000/ideas/"

Write-Output ""
Write-Output "--- GET /ideas/{idea_id} output ---"
curl.exe -s -X GET "http://localhost:8000/ideas/$ideaId"

Write-Output ""
Write-Output "--- GET /ideas/{idea_id}/agents/idea_validator output ---"
curl.exe -s -X GET "http://localhost:8000/ideas/$ideaId/agents/idea_validator"
