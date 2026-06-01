@description('Globally unique Microsoft Foundry resource name. Lowercase letters, numbers, and hyphens are safest.')
param aiFoundryName string

@description('Project name under the Foundry resource.')
param aiProjectName string

@description('Azure region for the Foundry resource.')
param location string = resourceGroup().location

@description('Disable key-based local auth so the app uses Entra ID / az login via DefaultAzureCredential.')
param disableLocalAuth bool = true

@description('Optional low-cost model deployment name. Leave empty to deploy no model.')
param modelDeploymentName string = ''

@description('Optional model name, for example gpt-5.4-nano or gpt-5.4-mini.')
param modelName string = 'gpt-5.4-nano'

@description('Optional model version.')
param modelVersion string = '2026-03-17'

@description('Use token-based standard deployment. Keep capacity at 1 for the smallest rate limit.')
param modelSkuName string = 'GlobalStandard'

@description('Smallest deployment capacity to reduce token-per-minute exposure.')
@minValue(1)
@maxValue(1)
param modelSkuCapacity int = 1

resource aiFoundry 'Microsoft.CognitiveServices/accounts@2025-06-01' = {
  name: aiFoundryName
  location: location
  identity: {
    type: 'SystemAssigned'
  }
  sku: {
    name: 'S0'
  }
  kind: 'AIServices'
  properties: {
    allowProjectManagement: true
    customSubDomainName: aiFoundryName
    disableLocalAuth: disableLocalAuth
  }
}

resource aiProject 'Microsoft.CognitiveServices/accounts/projects@2025-06-01' = {
  name: aiProjectName
  parent: aiFoundry
  location: location
  identity: {
    type: 'SystemAssigned'
  }
  properties: {}
}

resource modelDeployment 'Microsoft.CognitiveServices/accounts/deployments@2025-06-01' = if (!empty(modelDeploymentName)) {
  parent: aiFoundry
  name: modelDeploymentName
  sku: {
    name: modelSkuName
    capacity: modelSkuCapacity
  }
  properties: {
    model: {
      name: modelName
      format: 'OpenAI'
      version: modelVersion
    }
  }
}

output aiFoundryName string = aiFoundry.name
output aiProjectName string = aiProject.name
output modelDeploymentName string = empty(modelDeploymentName) ? '' : modelDeployment.name
output projectEndpoint string = 'https://${aiFoundryName}.services.ai.azure.com/api/projects/${aiProjectName}'
output alternateProjectEndpoint string = 'https://${aiFoundryName}.ai.azure.com/api/projects/${aiProjectName}'
