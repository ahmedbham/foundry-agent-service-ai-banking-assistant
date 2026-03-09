targetScope = 'subscription'

@minLength(1)
@maxLength(64)
@description('Name of the environment (used to generate unique resource names)')
param environmentName string

@description('Primary location for all resources')
param location string

@description('Name for the Foundry (AI Services) account')
param foundryAccountName string = ''

@description('Name for the Foundry project')
param foundryProjectName string = ''

@description('Name for the Azure Container Registry')
param containerRegistryName string = ''

@description('Name for the Container Apps Environment')
param containerAppsEnvName string = ''

@description('Name for the backend Container App')
param backendAppName string = ''

@description('Name for the middle tier Container App')
param middleAppName string = ''

@description('Name for the frontend Container App')
param frontendAppName string = ''

@description('Name for the resource group')
param resourceGroupName string = ''

var abbrs = {
  resourceGroup: 'rg-'
  cognitiveServices: 'ai-'
  containerRegistry: 'cr'
  containerAppsEnv: 'cae-'
  containerApp: 'ca-'
  logAnalytics: 'log-'
}

var resourceToken = toLower(uniqueString(subscription().id, environmentName, location))
var _resourceGroupName = !empty(resourceGroupName) ? resourceGroupName : '${abbrs.resourceGroup}${environmentName}'
var _foundryAccountName = !empty(foundryAccountName) ? foundryAccountName : '${abbrs.cognitiveServices}${resourceToken}'
var _foundryProjectName = !empty(foundryProjectName) ? foundryProjectName : 'banking-assistant'
var _containerRegistryName = !empty(containerRegistryName) ? containerRegistryName : '${abbrs.containerRegistry}${resourceToken}'
var _containerAppsEnvName = !empty(containerAppsEnvName) ? containerAppsEnvName : '${abbrs.containerAppsEnv}${resourceToken}'
var _backendAppName = !empty(backendAppName) ? backendAppName : '${abbrs.containerApp}backend-${resourceToken}'
var _middleAppName = !empty(middleAppName) ? middleAppName : '${abbrs.containerApp}middle-${resourceToken}'
var _frontendAppName = !empty(frontendAppName) ? frontendAppName : '${abbrs.containerApp}frontend-${resourceToken}'

resource rg 'Microsoft.Resources/resourceGroups@2024-03-01' = {
  name: _resourceGroupName
  location: location
}

module resources 'resources.bicep' = {
  name: 'resources'
  scope: rg
  params: {
    location: location
    foundryAccountName: _foundryAccountName
    foundryProjectName: _foundryProjectName
    containerRegistryName: _containerRegistryName
    containerAppsEnvName: _containerAppsEnvName
    backendAppName: _backendAppName
    middleAppName: _middleAppName
    frontendAppName: _frontendAppName
  }
}

output AZURE_RESOURCE_GROUP string = rg.name
output AZURE_CONTAINER_REGISTRY_ENDPOINT string = resources.outputs.containerRegistryLoginServer
output AZURE_CONTAINER_REGISTRY_NAME string = resources.outputs.containerRegistryName
output BACKEND_APP_URL string = resources.outputs.backendAppUrl
output FOUNDRY_ENDPOINT string = resources.outputs.foundryEndpoint
output FOUNDRY_PROJECT_NAME string = resources.outputs.foundryProjectName
output SERVICE_BACKEND_RESOURCE_ID string = resources.outputs.backendAppId
output MIDDLE_APP_URL string = resources.outputs.middleAppUrl
output SERVICE_MIDDLE_RESOURCE_ID string = resources.outputs.middleAppId
output FRONTEND_APP_URL string = resources.outputs.frontendAppUrl
output SERVICE_FRONTEND_RESOURCE_ID string = resources.outputs.frontendAppId
