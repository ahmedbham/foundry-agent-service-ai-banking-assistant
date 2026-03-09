param location string
param foundryAccountName string
param foundryProjectName string
param containerRegistryName string
param containerAppsEnvName string
param backendAppName string
param middleAppName string

// ── Log Analytics ──────────────────────────────────────────────────
resource logAnalytics 'Microsoft.OperationalInsights/workspaces@2023-09-01' = {
  name: 'log-${uniqueString(resourceGroup().id)}'
  location: location
  properties: {
    sku: { name: 'PerGB2018' }
    retentionInDays: 30
  }
}

// ── Foundry (AI Services) ─────────────────────────────────────────
resource foundry 'Microsoft.CognitiveServices/accounts@2025-10-01-preview' = {
  name: foundryAccountName
  location: location
  kind: 'AIServices'
  identity: { type: 'SystemAssigned' }
  sku: { name: 'S0' }
  properties: {
    customSubDomainName: foundryAccountName
    publicNetworkAccess: 'Enabled'
    allowProjectManagement: true
  }

  resource project 'projects' = {
    name: foundryProjectName
    location: location
    identity: { type: 'SystemAssigned' }
    properties: {}
  }

  resource model 'deployments' = {
    name: 'agent-model'
    sku: {
      capacity: 10
      name: 'GlobalStandard'
    }
    properties: {
      model: {
        format: 'OpenAI'
        name: 'gpt-4.1'
        version: '2025-04-14'
      }
      raiPolicyName: 'Microsoft.DefaultV2'
    }
  }
}

// ── Container Registry ────────────────────────────────────────────
resource acr 'Microsoft.ContainerRegistry/registries@2023-07-01' = {
  name: containerRegistryName
  location: location
  sku: { name: 'Basic' }
  properties: {
    adminUserEnabled: true
  }
}

// ── Container Apps Environment ────────────────────────────────────
resource containerAppsEnv 'Microsoft.App/managedEnvironments@2024-03-01' = {
  name: containerAppsEnvName
  location: location
  properties: {
    appLogsConfiguration: {
      destination: 'log-analytics'
      logAnalyticsConfiguration: {
        customerId: logAnalytics.properties.customerId
        sharedKey: logAnalytics.listKeys().primarySharedKey
      }
    }
  }
}

// ── Backend Container App ─────────────────────────────────────────
resource backendApp 'Microsoft.App/containerApps@2024-03-01' = {
  name: backendAppName
  location: location
  properties: {
    managedEnvironmentId: containerAppsEnv.id
    configuration: {
      ingress: {
        external: true
        targetPort: 8000
        transport: 'auto'
        allowInsecure: false
      }
      registries: [
        {
          server: acr.properties.loginServer
          username: acr.listCredentials().username
          passwordSecretRef: 'acr-password'
        }
      ]
      secrets: [
        {
          name: 'acr-password'
          value: acr.listCredentials().passwords[0].value
        }
      ]
    }
    template: {
      containers: [
        {
          name: 'backend'
          image: '${acr.properties.loginServer}/backend:latest'
          resources: {
            cpu: json('0.5')
            memory: '1Gi'
          }
        }
      ]
      scale: {
        minReplicas: 0
        maxReplicas: 3
      }
    }
  }
}

// ── Middle Tier Container App ────────────────────────────────────────
resource middleApp 'Microsoft.App/containerApps@2024-03-01' = {
  name: middleAppName
  location: location
  identity: { type: 'SystemAssigned' }
  properties: {
    managedEnvironmentId: containerAppsEnv.id
    configuration: {
      ingress: {
        external: true
        targetPort: 8000
        transport: 'auto'
        allowInsecure: false
      }
      registries: [
        {
          server: acr.properties.loginServer
          username: acr.listCredentials().username
          passwordSecretRef: 'acr-password'
        }
      ]
      secrets: [
        {
          name: 'acr-password'
          value: acr.listCredentials().passwords[0].value
        }
      ]
    }
    template: {
      containers: [
        {
          name: 'middle'
          image: '${acr.properties.loginServer}/middle:latest'
          resources: {
            cpu: json('0.5')
            memory: '1Gi'
          }
          env: [
            {
              name: 'FOUNDRY_ENDPOINT'
              value: 'https://${foundryAccountName}.services.ai.azure.com/api/projects/${foundryProjectName}'
            }
            {
              name: 'BACKEND_MCP_URL'
              value: 'https://${backendApp.properties.configuration.ingress.fqdn}/mcp/mcp'
            }
            {
              name: 'MODEL_DEPLOYMENT_NAME'
              value: 'agent-model'
            }
          ]
        }
      ]
      scale: {
        minReplicas: 0
        maxReplicas: 3
      }
    }
  }
}

// ── RBAC: Middle tier → Foundry (Cognitive Services User) ─────────
resource middleToFoundryRole 'Microsoft.Authorization/roleAssignments@2022-04-01' = {
  name: guid(middleApp.id, foundry.id, 'CognitiveServicesUser')
  scope: foundry
  properties: {
    principalId: middleApp.identity.principalId
    principalType: 'ServicePrincipal'
    roleDefinitionId: subscriptionResourceId('Microsoft.Authorization/roleDefinitions', 'a97b65f3-24c7-4388-baec-2e87135dc908')
  }
}

output containerRegistryLoginServer string = acr.properties.loginServer
output containerRegistryName string = acr.name
output backendAppId string = backendApp.id
output backendAppUrl string = 'https://${backendApp.properties.configuration.ingress.fqdn}'
output middleAppId string = middleApp.id
output middleAppUrl string = 'https://${middleApp.properties.configuration.ingress.fqdn}'
output foundryEndpoint string = 'https://${foundryAccountName}.services.ai.azure.com/api/projects/${foundryProjectName}'
output foundryProjectName string = foundryProjectName
