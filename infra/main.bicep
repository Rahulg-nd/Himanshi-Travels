// Main Bicep template for Himanshi Travels Flask application deployment
// Deploys App Service Plan and App Service with Python runtime
targetScope = 'resourceGroup'

// Parameters
@description('Name of the environment (dev, staging, prod)')
param environmentName string = 'dev'

@description('Primary location for all resources')
param location string = resourceGroup().location

@description('Name of the application')
param appName string = 'himanshi-travels'

@description('SKU for the App Service Plan')
@allowed([
  'F1'  // Free tier
  'B1'  // Basic tier
  'S1'  // Standard tier
  'P1v2' // Premium v2 tier
  'P1v3' // Premium v3 tier
])
param appServicePlanSku string = 'F1'

@description('Python version for the App Service')
@allowed([
  '3.8'
  '3.9'
  '3.10'
  '3.11'
  '3.12'
])
param pythonVersion string = '3.11'

// Variables
var resourceToken = toLower(uniqueString(subscription().id, environmentName, location))
var appServicePlanName = '${appName}-plan-${resourceToken}'
var webAppName = '${appName}-${resourceToken}'
var tags = {
  'azd-env-name': environmentName
  'azd-service-name': 'web'
  'app-name': appName
  'environment': environmentName
}

// App Service Plan
resource appServicePlan 'Microsoft.Web/serverfarms@2024-11-01' = {
  name: appServicePlanName
  location: location
  kind: 'linux'
  tags: tags
  properties: {
    reserved: true // Required for Linux plans
  }
  sku: {
    name: appServicePlanSku
    tier: appServicePlanSku == 'F1' ? 'Free' : (appServicePlanSku == 'B1' ? 'Basic' : (appServicePlanSku == 'S1' ? 'Standard' : 'Premium'))
    capacity: 1
  }
}

// Web App (App Service)
resource webApp 'Microsoft.Web/sites@2024-11-01' = {
  name: webAppName
  location: location
  kind: 'app,linux'
  tags: tags
  identity: {
    type: 'SystemAssigned'
  }
  properties: {
    serverFarmId: appServicePlan.id
    httpsOnly: true
    clientAffinityEnabled: false
    
    siteConfig: {
      // Python runtime configuration
      linuxFxVersion: 'PYTHON|${pythonVersion}'
      
      // Application settings
      appSettings: [
        {
          name: 'SCM_DO_BUILD_DURING_DEPLOYMENT'
          value: 'true'
        }
        {
          name: 'ENABLE_ORYX_BUILD'
          value: 'true'
        }
        {
          name: 'PYTHONPATH'
          value: '/home/site/wwwroot'
        }
        {
          name: 'FLASK_APP'
          value: 'app.py'
        }
        {
          name: 'FLASK_ENV'
          value: 'production'
        }
        {
          name: 'PORT'
          value: '8000'
        }
        {
          name: 'WEBSITES_PORT'
          value: '8000'
        }
      ]
      
      // Web server configuration
      alwaysOn: appServicePlanSku != 'F1' // Always On not available in Free tier
      httpLoggingEnabled: true
      detailedErrorLoggingEnabled: true
      requestTracingEnabled: true
      
      // Health check configuration
      healthCheckPath: '/'
      
      // Default documents
      defaultDocuments: [
        'app.py'
        'main.py'
        'index.html'
      ]
      
      // CORS settings (allow all origins for now)
      cors: {
        allowedOrigins: ['*']
        supportCredentials: false
      }
      
      // Auto heal settings for better reliability
      autoHealEnabled: true
      autoHealRules: {
        triggers: {
          requests: {
            count: 100
            timeInterval: '00:05:00'
          }
          privateBytesInKB: 0
          statusCodes: [
            {
              status: 500
              subStatus: 0
              win32Status: 0
              count: 10
              timeInterval: '00:05:00'
            }
          ]
        }
        actions: {
          actionType: 'Recycle'
          minProcessExecutionTime: '00:01:00'
        }
      }
    }
  }
}

// Outputs
@description('The default hostname of the web app')
output webAppHostName string = webApp.properties.defaultHostName

@description('The URL of the web app')
output webAppUrl string = 'https://${webApp.properties.defaultHostName}'

@description('The name of the web app')
output webAppName string = webApp.name

@description('The resource ID of the web app')
output webAppId string = webApp.id

@description('The principal ID of the system assigned managed identity')
output webAppPrincipalId string = webApp.identity.principalId
