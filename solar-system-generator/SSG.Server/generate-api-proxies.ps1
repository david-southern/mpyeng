$restArgs = @{
    Uri         = 'http://localhost:5153/api/codegen'
    Method      = 'Post'
    InFile      = ".\CodeGen.json"
    ContentType = 'application/json'
}
Invoke-RestMethod @restArgs