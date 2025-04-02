# Azure Identity client library for Python

The Azure Identity library provides [Microsoft Entra ID](https://learn.microsoft.com/entra/fundamentals/whatis) ([formerly Azure Active Directory](https://learn.microsoft.com/entra/fundamentals/new-name)) token authentication support across the Azure SDK. It provides a set of [`TokenCredential`][token_cred_ref]/[`SupportsTokenInfo`][supports_token_info_ref] implementations, which can be used to construct Azure SDK clients that support Microsoft Entra token authentication.

[Source code](https://github.com/Azure/azure-sdk-for-python/blob/main/sdk/identity/azure-identity)
| [Package (PyPI)](https://pypi.org/project/azure-identity/)
| [Package (Conda)](https://anaconda.org/microsoft/azure-identity/)
| [API reference documentation][ref_docs]
| [Microsoft Entra ID documentation](https://learn.microsoft.com/entra/identity/)

## Getting started

### Install the package

Install Azure Identity with pip:

```sh
pip install azure-identity
```

### Prerequisites

- An [Azure subscription](https://azure.microsoft.com/free/python)
- Python 3.8 or a recent version of Python 3 (this library doesn't support end-of-life versions)

### Authenticate during local development

When debugging and executing code locally, it's typical for developers to use their own accounts for authenticating calls to Azure services. The Azure Identity library supports authenticating through developer tools to simplify local development.

#### Authenticate via Visual Studio Code

Developers using Visual Studio Code can use the [Azure Account extension](https://marketplace.visualstudio.com/items?itemName=ms-vscode.azure-account) to authenticate via the editor. Apps using `DefaultAzureCredential` or `VisualStudioCodeCredential` can then use this account to authenticate calls in their app when running locally.

To authenticate in Visual Studio Code, ensure the Azure Account extension is installed. Once installed, open the **Command Palette** and run the **Azure: Sign In** command.

It's a [known issue](https://github.com/Azure/azure-sdk-for-python/issues/23249) that `VisualStudioCodeCredential` doesn't work with [Azure Account extension](https://marketplace.visualstudio.com/items?itemName=ms-vscode.azure-account) versions newer than **0.9.11**. A long-term fix to this problem is in progress. In the meantime, consider [authenticating via the Azure CLI](#authenticate-via-the-azure-cli).

#### Authenticate via the Azure CLI

`DefaultAzureCredential` and `AzureCliCredential` can authenticate as the user signed in to the [Azure CLI][azure_cli]. To sign in to the Azure CLI, run `az login`. On a system with a default web browser, the Azure CLI launches the browser to authenticate a user.

When no default browser is available, `az login` uses the device code authentication flow. This flow can also be selected manually by running `az login --use-device-code`.

#### Authenticate via the Azure Developer CLI

Developers coding outside of an IDE can also use the [Azure Developer CLI][azure_developer_cli] to authenticate. Applications using `DefaultAzureCredential` or `AzureDeveloperCliCredential` can then use this account to authenticate calls in their application when running locally.

To authenticate with the [Azure Developer CLI][azure_developer_cli], run the command `azd auth login`. For users running on a system with a default web browser, the Azure Developer CLI launches the browser to authenticate the user.

For systems without a default web browser, the `azd auth login --use-device-code` command uses the device code authentication flow.

## Key concepts

### Credentials

A credential is a class that contains or can obtain the data needed for a service client to authenticate requests. Service clients across the Azure SDK accept a credential instance when they're constructed, and use that credential to authenticate requests.

The Azure Identity library focuses on OAuth authentication with Microsoft Entra ID. It offers various credential classes capable of acquiring a Microsoft Entra access token. See the [Credential classes](#credential-classes "Credential classes") section for a list of this library's credential classes.

### DefaultAzureCredential

`DefaultAzureCredential` simplifies authentication while developing apps that deploy to Azure by combining credentials used in Azure hosting environments with credentials used in local development. For more information, see [DefaultAzureCredential overview][dac_overview].

#### Continuation policy

As of version 1.14.0, `DefaultAzureCredential` attempts to authenticate with all developer credentials until one succeeds, regardless of any errors previous developer credentials experienced. For example, a developer credential may attempt to get a token and fail, so `DefaultAzureCredential` will continue to the next credential in the flow. Deployed service credentials stop the flow with a thrown exception if they're able to attempt token retrieval, but don't receive one. Prior to version 1.14.0, developer credentials would similarly stop the authentication flow if token retrieval failed, but this is no longer the case.

This allows for trying all of the developer credentials on your machine while having predictable deployed behavior.

#### Note about `VisualStudioCodeCredential`

Due to a [known issue](https://github.com/Azure/azure-sdk-for-python/issues/23249), `VisualStudioCodeCredential` has been removed from the `DefaultAzureCredential` token chain. When the issue is resolved in a future release, this change will be reverted.

## Examples

The following examples are provided:

- [Authenticate with DefaultAzureCredential](#authenticate-with-defaultazurecredential "Authenticate with DefaultAzureCredential")
- [Define a custom authentication flow with ChainedTokenCredential](#define-a-custom-authentication-flow-with-chainedtokencredential "Define a custom authentication flow with ChainedTokenCredential")
- [Async credentials](#async-credentials "Async credentials")

### Authenticate with `DefaultAzureCredential`

More details on configuring your environment to use `DefaultAzureCredential` can be found in the class's [reference documentation][default_cred_ref].

This example demonstrates authenticating the `BlobServiceClient` from the [azure-storage-blob][azure_storage_blob] library using `DefaultAzureCredential`.

```python
from azure.identity import DefaultAzureCredential
from azure.storage.blob import BlobServiceClient

default_credential = DefaultAzureCredential()

client = BlobServiceClient(account_url, credential=default_credential)
```

#### Enable interactive authentication with `DefaultAzureCredential`

By default, interactive authentication is disabled in `DefaultAzureCredential` and can be enabled with a keyword argument:

```python
DefaultAzureCredential(exclude_interactive_browser_credential=False)
```

When enabled, `DefaultAzureCredential` falls back to interactively authenticating via the system's default web browser when no other credential is available.

#### Specify a user-assigned managed identity with `DefaultAzureCredential`

Many Azure hosts allow the assignment of a user-assigned managed identity. To configure `DefaultAzureCredential` to authenticate a user-assigned managed identity, use the `managed_identity_client_id` keyword argument:

```python
DefaultAzureCredential(managed_identity_client_id=client_id)
```

Alternatively, set the environment variable `AZURE_CLIENT_ID` to the identity's client ID.

### Define a custom authentication flow with `ChainedTokenCredential`

While `DefaultAzureCredential` is generally the quickest way to authenticate apps for Azure, you can create a customized chain of credentials to be considered. `ChainedTokenCredential` enables users to combine multiple credential instances to define a customized chain of credentials. For more information, see [ChainedTokenCredential overview][ctc_overview].

### Async credentials

This library includes a set of async APIs. To use the async credentials in [azure.identity.aio][ref_docs_aio], you must first install an async transport, such as [aiohttp](https://pypi.org/project/aiohttp/). For more information, see [azure-core documentation][azure_core_transport_doc].

Async credentials should be closed when they're no longer needed. Each async credential is an async context manager and defines an async `close` method. For example:

```python
from azure.identity.aio import DefaultAzureCredential

# call close when the credential is no longer needed
credential = DefaultAzureCredential()
...
await credential.close()

# alternatively, use the credential as an async context manager
credential = DefaultAzureCredential()
async with credential:
  ...
```

This example demonstrates authenticating the asynchronous `SecretClient` from [azure-keyvault-secrets][azure_keyvault_secrets] with an asynchronous credential.

```python
from azure.identity.aio import DefaultAzureCredential
from azure.keyvault.secrets.aio import SecretClient

default_credential = DefaultAzureCredential()
client = SecretClient("https://my-vault.vault.azure.net", default_credential)
```

## Managed identity support

[Managed identity authentication](https://learn.microsoft.com/entra/identity/managed-identities-azure-resources/overview) is supported via either `DefaultAzureCredential` or `ManagedIdentityCredential` directly for the following Azure services:

- [Azure App Service and Azure Functions](https://learn.microsoft.com/azure/app-service/overview-managed-identity?tabs=python)
- [Azure Arc](https://learn.microsoft.com/azure/azure-arc/servers/managed-identity-authentication)
- [Azure Cloud Shell](https://learn.microsoft.com/azure/cloud-shell/msi-authorization)
- [Azure Kubernetes Service](https://learn.microsoft.com/azure/aks/use-managed-identity)
- [Azure Service Fabric](https://learn.microsoft.com/azure/service-fabric/concepts-managed-identity)
- [Azure Virtual Machines](https://learn.microsoft.com/entra/identity/managed-identities-azure-resources/how-to-use-vm-token)
- [Azure Virtual Machines Scale Sets](https://learn.microsoft.com/entra/identity/managed-identities-azure-resources/qs-configure-powershell-windows-vmss)

### Examples

These examples demonstrate authenticating `SecretClient` from the [`azure-keyvault-secrets`](https://github.com/Azure/azure-sdk-for-python/tree/main/sdk/keyvault/azure-keyvault-secrets) library with `ManagedIdentityCredential`.

#### Authenticate with a user-assigned managed identity

To authenticate with a user-assigned managed identity, you must specify one of the following IDs for the managed identity.

##### Client ID

```python
from azure.identity import ManagedIdentityCredential
from azure.keyvault.secrets import SecretClient

credential = ManagedIdentityCredential(client_id="managed_identity_client_id")
client = SecretClient("https://my-vault.vault.azure.net", credential)
```

##### Resource ID

```python
from azure.identity import ManagedIdentityCredential
from azure.keyvault.secrets import SecretClient

resource_id = "/subscriptions/<id>/resourceGroups/<rg>/providers/Microsoft.ManagedIdentity/userAssignedIdentities/<mi-name>"

credential = ManagedIdentityCredential(identity_config={"resource_id": resource_id})
client = SecretClient("https://my-vault.vault.azure.net", credential)
```

##### Object ID

```python
from azure.identity import ManagedIdentityCredential
from azure.keyvault.secrets import SecretClient

credential = ManagedIdentityCredential(identity_config={"object_id": "managed_identity_object_id"})
client = SecretClient("https://my-vault.vault.azure.net", credential)
```

#### Authenticate with a system-assigned managed identity

```python
from azure.identity import ManagedIdentityCredential
from azure.keyvault.secrets import SecretClient

credential = ManagedIdentityCredential()
client = SecretClient("https://my-vault.vault.azure.net", credential)
```

## Cloud configuration

Credentials default to authenticating to the Microsoft Entra endpoint for Azure Public Cloud. To access resources in other clouds, such as Azure Government or a private cloud, configure credentials with the `authority` argument. [AzureAuthorityHosts](https://aka.ms/azsdk/python/identity/docs#azure.identity.AzureAuthorityHosts) defines authorities for well-known clouds:

```python
from azure.identity import AzureAuthorityHosts

DefaultAzureCredential(authority=AzureAuthorityHosts.AZURE_GOVERNMENT)
```

If the authority for your cloud isn't listed in `AzureAuthorityHosts`, you can explicitly specify its URL:

```python
DefaultAzureCredential(authority="https://login.partner.microsoftonline.cn")
```

As an alternative to specifying the `authority` argument, you can also set the `AZURE_AUTHORITY_HOST` environment variable to the URL of your cloud's authority. This approach is useful when configuring multiple credentials to authenticate to the same cloud:

```sh
AZURE_AUTHORITY_HOST=https://login.partner.microsoftonline.cn
```

Not all credentials require this configuration. Credentials that authenticate through a development tool, such as `AzureCliCredential`, use that tool's configuration. Similarly, `VisualStudioCodeCredential` accepts an `authority` argument but defaults to the authority matching VS Code's "Azure: Cloud" setting.

## Credential classes

### Credential chains

| Credential                                   | Usage                                                                                                  |
| -------------------------------------------- | ------------------------------------------------------------------------------------------------------ |
| [`DefaultAzureCredential`][default_cred_ref] | Provides a simplified authentication experience to quickly start developing applications run in Azure. |
| [`ChainedTokenCredential`][chain_cred_ref]   | Allows users to define custom authentication flows composing multiple credentials.                     |

### Authenticate Azure-hosted applications

| Credential                                           | Usage                                                                                                                   |
| ---------------------------------------------------- | ----------------------------------------------------------------------------------------------------------------------- |
| [`EnvironmentCredential`][environment_cred_ref]      | Authenticates a service principal or user via credential information specified in environment variables.                |
| [`ManagedIdentityCredential`][managed_id_cred_ref]   | Authenticates the managed identity of an Azure resource.                                                                |
| [`WorkloadIdentityCredential`][workload_id_cred_ref] | Supports [Microsoft Entra Workload ID](https://learn.microsoft.com/azure/aks/workload-identity-overview) on Kubernetes. |

### Authenticate service principals

| Credential                                               | Usage                                                                                                                                                                | Reference                                                                                                                  |
| -------------------------------------------------------- | -------------------------------------------------------------------------------------------------------------------------------------------------------------------- | -------------------------------------------------------------------------------------------------------------------------- |
| [`AzurePipelinesCredential`][az_pipelines_cred_ref]      | Supports [Microsoft Entra Workload ID](https://learn.microsoft.com/azure/devops/pipelines/release/configure-workload-identity?view=azure-devops) on Azure Pipelines. |
| [`CertificateCredential`][cert_cred_ref]                 | Authenticates a service principal using a certificate.                                                                                                               | [Service principal authentication](https://learn.microsoft.com/entra/identity-platform/app-objects-and-service-principals) |
| [`ClientAssertionCredential`][client_assertion_cred_ref] | Authenticates a service principal using a signed client assertion.                                                                                                   |
| [`ClientSecretCredential`][client_secret_cred_ref]       | Authenticates a service principal using a secret.                                                                                                                    | [Service principal authentication](https://learn.microsoft.com/entra/identity-platform/app-objects-and-service-principals) |

### Authenticate users

| Credential                                             | Usage                                                                             | Reference                                                                                                      | Notes                                                                                                                                  |
| ------------------------------------------------------ | --------------------------------------------------------------------------------- | -------------------------------------------------------------------------------------------------------------- | -------------------------------------------------------------------------------------------------------------------------------------- |
| [`AuthorizationCodeCredential`][auth_code_cred_ref]    | Authenticates a user with a previously obtained authorization code.               | [OAuth2 authentication code](https://learn.microsoft.com/entra/identity-platform/v2-oauth2-auth-code-flow)     |
| [`DeviceCodeCredential`][device_code_cred_ref]         | Interactively authenticates a user on devices with limited UI.                    | [Device code authentication](https://learn.microsoft.com/entra/identity-platform/v2-oauth2-device-code)        |
| [`InteractiveBrowserCredential`][interactive_cred_ref] | Interactively authenticates a user with the default system browser.               | [OAuth2 authentication code](https://learn.microsoft.com/entra/identity-platform/v2-oauth2-auth-code-flow)     | `InteractiveBrowserCredential` doesn't support GitHub Codespaces. As a workaround, use [`DeviceCodeCredential`][device_code_cred_ref]. |
| [`OnBehalfOfCredential`][obo_cred_ref]                 | Propagates the delegated user identity and permissions through the request chain. | [On-behalf-of authentication](https://learn.microsoft.com/entra/identity-platform/v2-oauth2-on-behalf-of-flow) |

### Authenticate via development tools

| Credential                                         | Usage                                                                                  | Reference                                                                                                      |
| -------------------------------------------------- | -------------------------------------------------------------------------------------- | -------------------------------------------------------------------------------------------------------------- |
| [`AzureCliCredential`][cli_cred_ref]               | Authenticates in a development environment with the Azure CLI.                         | [Azure CLI authentication](https://learn.microsoft.com/cli/azure/authenticate-azure-cli)                       |
| [`AzureDeveloperCliCredential`][azd_cli_cred_ref]  | Authenticates in a development environment with the Azure Developer CLI.               | [Azure Developer CLI Reference](https://learn.microsoft.com/azure/developer/azure-developer-cli/reference)     |
| [`AzurePowerShellCredential`][powershell_cred_ref] | Authenticates in a development environment with the Azure PowerShell.                  | [Azure PowerShell authentication](https://learn.microsoft.com/powershell/azure/authenticate-azureps)           |
| [`VisualStudioCodeCredential`][vscode_cred_ref]    | Authenticates as the user signed in to the Visual Studio Code Azure Account extension. | [VS Code Azure Account extension](https://marketplace.visualstudio.com/items?itemName=ms-vscode.azure-account) |

## Environment variables

[DefaultAzureCredential][default_cred_ref] and [EnvironmentCredential][environment_cred_ref] can be configured with environment variables. Each type of authentication requires values for specific
variables:

### Service principal with secret

| Variable name         | Value                                          |
| --------------------- | ---------------------------------------------- |
| `AZURE_CLIENT_ID`     | ID of a Microsoft Entra application            |
| `AZURE_TENANT_ID`     | ID of the application's Microsoft Entra tenant |
| `AZURE_CLIENT_SECRET` | one of the application's client secrets        |

### Service principal with certificate

| Variable name                         | Value                                                                                                                                                                                                                                                                                                                                 | Required |
| ------------------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | -------- |
| `AZURE_CLIENT_ID`                     | ID of a Microsoft Entra application                                                                                                                                                                                                                                                                                                   | X        |
| `AZURE_TENANT_ID`                     | ID of the application's Microsoft Entra tenant                                                                                                                                                                                                                                                                                        | X        |
| `AZURE_CLIENT_CERTIFICATE_PATH`       | path to a PEM or PKCS12 certificate file including private key                                                                                                                                                                                                                                                                        | X        |
| `AZURE_CLIENT_CERTIFICATE_PASSWORD`   | password of the certificate file, if any                                                                                                                                                                                                                                                                                              |
| `AZURE_CLIENT_SEND_CERTIFICATE_CHAIN` | If `True`, the credential sends the public certificate chain in the x5c header of each token request's JWT. This is required for Subject Name/Issuer (SNI) authentication. Defaults to False. There's a [known limitation](https://github.com/Azure/azure-sdk-for-python/issues/13349) that async SNI authentication isn't supported. |

Configuration is attempted in the preceding order. For example, if values for a client secret and certificate are both present, the client secret is used.

## Continuous Access Evaluation

As of version 1.14.0, accessing resources protected by [Continuous Access Evaluation (CAE)][cae] is possible on a per-request basis. This behavior can be enabled by setting the `enable_cae` keyword argument to `True` in the credential's `get_token` method. CAE isn't supported for developer and managed identity credentials.

## Token caching

Token caching is a feature provided by the Azure Identity library that allows apps to:

- Cache tokens in memory (default) or on disk (opt-in).
- Improve resilience and performance.
- Reduce the number of requests made to Microsoft Entra ID to obtain access tokens.

The Azure Identity library offers both in-memory and persistent disk caching. For more information, see the [token caching documentation](https://github.com/Azure/azure-sdk-for-python/blob/main/sdk/identity/azure-identity/TOKEN_CACHING.md).

## Brokered authentication

An authentication broker is an application that runs on a user’s machine and manages the authentication handshakes and token maintenance for connected accounts. Currently, only the Windows Web Account Manager (WAM) is supported. To enable support, use the [`azure-identity-broker`][azure_identity_broker] package. For details on authenticating using WAM, see the [broker plugin documentation][azure_identity_broker_readme].

## Troubleshooting

See the [troubleshooting guide][troubleshooting_guide] for details on how to diagnose various failure scenarios.

### Error handling

Credentials raise `CredentialUnavailableError` when they're unable to attempt authentication because they lack required data or state. For example, [EnvironmentCredential][environment_cred_ref] raises this exception when [its configuration](#environment-variables "its configuration") is incomplete.

Credentials raise `azure.core.exceptions.ClientAuthenticationError` when they fail to authenticate. `ClientAuthenticationError` has a `message` attribute, which describes why authentication failed. When raised by `DefaultAzureCredential` or `ChainedTokenCredential`, the message collects error messages from each credential in the chain.

For more information on handling specific Microsoft Entra ID errors, see the Microsoft Entra ID [error code documentation](https://learn.microsoft.com/entra/identity-platform/reference-error-codes).

### Logging

This library uses the standard [logging](https://docs.python.org/3/library/logging.html) library for logging. Credentials log basic information, including HTTP sessions (URLs, headers, etc.) at INFO level. These log entries don't contain authentication secrets.

Detailed DEBUG-level logging, including request/response bodies and header values, isn't enabled by default. It can be enabled with the `logging_enable` argument. For example:

```python
credential = DefaultAzureCredential(logging_enable=True)
```

> CAUTION: DEBUG-level logs from credentials contain sensitive information.
> These logs must be protected to avoid compromising account security.

## Next steps

### Client library support

Client and management libraries listed on the [Azure SDK release page](https://azure.github.io/azure-sdk/releases/latest/python.html) that support Microsoft Entra authentication accept credentials from this library. You can learn more about using these libraries in their documentation, which is linked from the release page.

### Known issues

This library doesn't support [Azure AD B2C][b2c].

For other open issues, refer to the library's [GitHub repository](https://github.com/Azure/azure-sdk-for-python/issues?q=is%3Aopen+is%3Aissue+label%3AAzure.Identity).

### Provide feedback

If you encounter bugs or have suggestions, [open an issue](https://github.com/Azure/azure-sdk-for-python/issues).

## Contributing

This project welcomes contributions and suggestions. Most contributions require you to agree to a Contributor License Agreement (CLA) declaring that you have the right to, and actually do, grant us the rights to use your contribution. For details, visit [https://cla.microsoft.com](https://cla.microsoft.com).

When you submit a pull request, a CLA-bot will automatically determine whether you need to provide a CLA and decorate the PR appropriately (e.g., label, comment). Simply follow the instructions provided by the bot. You'll only need to do this once across all repos using our CLA.

This project has adopted the [Microsoft Open Source Code of Conduct](https://opensource.microsoft.com/codeofconduct/). For more information, see the [Code of Conduct FAQ](https://opensource.microsoft.com/codeofconduct/faq/) or contact [opencode@microsoft.com](mailto:opencode@microsoft.com) with any additional questions or comments.

[auth_code_cred_ref]: https://aka.ms/azsdk/python/identity/authorizationcodecredential
[az_pipelines_cred_ref]: https://aka.ms/azsdk/python/identity/azurepipelinescredential
[azd_cli_cred_ref]: https://aka.ms/azsdk/python/identity/azuredeveloperclicredential
[azure_cli]: https://learn.microsoft.com/cli/azure
[azure_developer_cli]: https://aka.ms/azure-dev
[azure_core_transport_doc]: https://github.com/Azure/azure-sdk-for-python/blob/main/sdk/core/azure-core/CLIENT_LIBRARY_DEVELOPER.md#transport
[azure_identity_broker]: https://pypi.org/project/azure-identity-broker
[azure_identity_broker_readme]: https://github.com/Azure/azure-sdk-for-python/tree/main/sdk/identity/azure-identity-broker
[azure_keyvault_secrets]: https://github.com/Azure/azure-sdk-for-python/blob/main/sdk/keyvault/azure-keyvault-secrets
[azure_storage_blob]: https://github.com/Azure/azure-sdk-for-python/blob/main/sdk/storage/azure-storage-blob
[b2c]: https://learn.microsoft.com/azure/active-directory-b2c/overview
[cae]: https://learn.microsoft.com/entra/identity/conditional-access/concept-continuous-access-evaluation
[cert_cred_ref]: https://aka.ms/azsdk/python/identity/certificatecredential
[chain_cred_ref]: https://aka.ms/azsdk/python/identity/chainedtokencredential
[cli_cred_ref]: https://aka.ms/azsdk/python/identity/azclicredential
[client_assertion_cred_ref]: https://aka.ms/azsdk/python/identity/clientassertioncredential
[client_secret_cred_ref]: https://aka.ms/azsdk/python/identity/clientsecretcredential
[ctc_overview]: https://aka.ms/azsdk/python/identity/credential-chains#chainedtokencredential-overview
[dac_overview]: https://aka.ms/azsdk/python/identity/credential-chains#defaultazurecredential-overview
[default_cred_ref]: https://aka.ms/azsdk/python/identity/defaultazurecredential
[device_code_cred_ref]: https://aka.ms/azsdk/python/identity/devicecodecredential
[environment_cred_ref]: https://aka.ms/azsdk/python/identity/environmentcredential
[interactive_cred_ref]: https://aka.ms/azsdk/python/identity/interactivebrowsercredential
[managed_id_cred_ref]: https://aka.ms/azsdk/python/identity/managedidentitycredential
[obo_cred_ref]: https://aka.ms/azsdk/python/identity/onbehalfofcredential
[powershell_cred_ref]: https://aka.ms/azsdk/python/identity/powershellcredential
[ref_docs]: https://aka.ms/azsdk/python/identity/docs
[ref_docs_aio]: https://aka.ms/azsdk/python/identity/aio/docs
[token_cred_ref]: https://learn.microsoft.com/python/api/azure-core/azure.core.credentials.tokencredential?view=azure-python
[supports_token_info_ref]: https://learn.microsoft.com/python/api/azure-core/azure.core.credentials.supportstokeninfo?view=azure-python
[troubleshooting_guide]: https://github.com/Azure/azure-sdk-for-python/blob/main/sdk/identity/azure-identity/TROUBLESHOOTING.md
[vscode_cred_ref]: https://aka.ms/azsdk/python/identity/vscodecredential
[workload_id_cred_ref]: https://aka.ms/azsdk/python/identity/workloadidentitycredential

### YamlMime:HowTo

metadata:
title: How to switch between OpenAI and Azure OpenAI Service endpoints with Python
titleSuffix: Azure OpenAI Service
description: Learn about the changes you need to make to your code to swap back and forth between OpenAI and Azure OpenAI endpoints.
author: mrbullwinkle
ms.author: mbullwin
manager: nitinme
ms.date: 03/27/2025
ms.service: azure-ai-openai
ms.topic: how-to
ms.custom: - devx-track-python - ge-structured-content-pilot
title: |
How to switch between OpenAI and Azure OpenAI endpoints with Python
introduction: |
While OpenAI and Azure OpenAI Service rely on a [common Python client library](https://github.com/openai/openai-python), there are small changes you need to make to your code in order to swap back and forth between endpoints. This article walks you through the common changes and differences you'll experience when working across OpenAI and Azure OpenAI.

This article only shows examples with the new OpenAI Python 1.x API library. For information on migrating from `0.28.1` to `1.x` refer to our [migration guide](./migration.md).
procedureSection:

- title: |
  Authentication
  summary: |
  We recommend using Microsoft Entra ID or Azure Key Vault. You can use environment variables for testing outside of your production environment. If you haven't done this before, our [Python quickstarts](../quickstart.md) walks you through this configuration.

  ### API key

  code: |
    <table>
    <tr>
    <td> OpenAI </td> <td> Azure OpenAI </td>
    </tr>
    <tr>
    <td>

  ```python
  import os
  from openai import OpenAI

  client = OpenAI(
      api_key=os.getenv("OPENAI_API_KEY")
  )



  ```

    </td>
    <td>

  ```python
  import os
  from openai import AzureOpenAI

  client = AzureOpenAI(
      api_key=os.getenv("AZURE_OPENAI_API_KEY"),
      api_version="2024-07-01-preview",
      azure_endpoint=os.getenv("AZURE_OPENAI_ENDPOINT")
  )
  ```

    </td>
    </tr>
    </table>

  <a name='azure-active-directory-authentication'></a>

  ### Microsoft Entra ID authentication

    <table>
    <tr>
    <td> OpenAI </td> <td> Azure OpenAI </td>
    </tr>
    <tr>
    <td>

  ```python
  import os
  from openai import OpenAI

  client = OpenAI(
      api_key=os.getenv("OPENAI_API_KEY")
  )








  ```

    </td>
    <td>

  ```python
  from azure.identity import DefaultAzureCredential, get_bearer_token_provider
  from openai import AzureOpenAI

  token_provider = get_bearer_token_provider(
      DefaultAzureCredential(), "https://cognitiveservices.azure.com/.default"
  )

  api_version = "2024-07-01-preview"
  endpoint = "https://my-resource.openai.azure.com"

  client = AzureOpenAI(
      api_version=api_version,
      azure_endpoint=endpoint,
      azure_ad_token_provider=token_provider,
  )
  ```

    </td>
    </tr>
    </table>

- title: |
  Keyword argument for model
  summary: |
  OpenAI uses the `model` keyword argument to specify what model to use. Azure OpenAI has the concept of unique model [deployments](create-resource.md?pivots=web-portal#deploy-a-model). When you use Azure OpenAI, `model` should refer to the underlying deployment name you chose when you deployed the model.

  > [!IMPORTANT]
  > When you access the model via the API in Azure OpenAI, you need to refer to the deployment name rather than the underlying model name in API calls, which is one of the [key differences](../how-to/switching-endpoints.yml) between OpenAI and Azure OpenAI. OpenAI only requires the model name. Azure OpenAI always requires deployment name, even when using the model parameter. In our docs, we often have examples where deployment names are represented as identical to model names to help indicate which model works with a particular API endpoint. Ultimately your deployment names can follow whatever naming convention is best for your use case.
  > code: |

    <table>
    <tr>
    <td> OpenAI </td> <td> Azure OpenAI </td>
    </tr>
    <tr>
    <td>

  ```python
  completion = client.completions.create(
      model="gpt-3.5-turbo-instruct",
      prompt="<prompt>"
  )

  chat_completion = client.chat.completions.create(
      model="gpt-4o",
      messages="<messages>"
  )

  embedding = client.embeddings.create(
      model="text-embedding-3-large",
      input="<input>"
  )
  ```

    </td>
    <td>

  ```python
  completion = client.completions.create(
      model="gpt-35-turbo-instruct", # This must match the custom deployment name you chose for your model.
      prompt="<prompt>"
  )

  chat_completion = client.chat.completions.create(
      model="gpt-4o", # model = "deployment_name".
      messages="<messages>"
  )

  embedding = client.embeddings.create(
      model="text-embedding-3-large", # model = "deployment_name".
      input="<input>"
  )
  ```

    </td>
    </tr>
    </table>

- title: |
  Azure OpenAI embeddings multiple input support
  summary: |
  OpenAI and Azure OpenAI currently support input arrays up to 2,048 input items for text-embedding-ada-002. Both require the max input token limit per API request to remain under 8,191 for this model.
  code: |
    <table>
    <tr>
    <td> OpenAI </td> <td> Azure OpenAI </td>
    </tr>
    <tr>
    <td>

  ```python
  inputs = ["A", "B", "C"]

  embedding = client.embeddings.create(
      input=inputs,
      model="text-embedding-3-large"
  )


  ```

    </td>
    <td>

  ```python
  inputs = ["A", "B", "C"] #max array size=2048

  embedding = client.embeddings.create(
      input=inputs,
      model="text-embedding-3-large" # This must match the custom deployment name you chose for your model.
      # engine="text-embedding-ada-002"
  )

  ```

    </td>
    </tr>
    </table>

relatedContent:

- text: Learn more about how to work with chat completions models with our how-to guide
  url: ../how-to/chatgpt.md
- text: For more examples, check out the Azure OpenAI Samples GitHub repository
  url: https://github.com/Azure-Samples/openai

# Learn more about how to work with GPT-35-Turbo and the GPT-4 models with [our how-to guide](../how-to/chatgpt.md).

# For more examples, check out the [Azure OpenAI Samples GitHub repository](https://github.com/Azure-Samples/openai)

---

title: Use keyless connections with Azure OpenAI
description: Use keyless connections for authentication and authorization to Azure OpenAI.
ms.topic: how-to
ms.date: 02/05/2025
ms.reviewer: scaddie
ms.custom: devx-track-extended-java, devx-track-js, devx-track-python, passwordless-dotnet, passwordless-java, passwordless-js, passwordless-python, passwordless-go, build-2024-intelligent-apps
#customer intent: As a developer, I want to use keyless connections so that I don't leak secrets.

---

# Use Azure OpenAI without keys

Application requests to most Azure services must be authenticated with keys or [passwordless connections](https://aka.ms/delete-passwords). Developers must be diligent to never expose the keys in an unsecure location. Anyone who gains access to the key is able to authenticate to the service. Keyless authentication offers improved management and security benefits over the account key because there's no key (or connection string) to store.

Keyless connections are enabled with the following steps:

- Configure your authentication.
- Set environment variables, as needed.
- Use an Azure Identity library credential type to create an Azure OpenAI client object.

## Authentication

Authentication to Microsoft Entra ID is required to use the Azure client libraries.

Authentication differs based on the environment in which the app is running:

- [Local development](#authenticate-for-local-development)
- [Azure](#authenticate-for-azure-hosted-environments)

## Azure OpenAI Keyless Building Block

Use the following link to explore the Azure OpenAI Keyless Building Block AI template. This template provisions an Azure OpenAI account with your user account RBAC role permission for keyless (Microsoft Entra) authentication to access the OpenAI API SDKs.

> [!NOTE]
> This article uses one or more [AI app templates](./intelligent-app-templates.md) as the basis for the examples and guidance in the article. AI app templates provide you with well-maintained, easy to deploy reference implementations that help to ensure a high-quality starting point for your AI apps.

### [.NET](#tab/csharp)

Explore the .NET [End to end Azure OpenAI Keyless Authentication Building Block AI template](https://github.com/Azure-Samples/azure-openai-keyless-csharp).

### [Go](#tab/go)

Explore the Go [End to end Azure OpenAI Keyless Authentication Building Block AI template](https://github.com/Azure-Samples/azure-openai-keyless-go).

### [Java](#tab/java)

Explore the Java [End to end Azure OpenAI Keyless Authentication Building Block AI template](https://github.com/Azure-Samples/azure-openai-keyless-java).

### [JavaScript](#tab/javascript)

Explore the JavaScript [End to end Azure OpenAI Keyless Authentication Building Block AI template](https://github.com/Azure-Samples/azure-openai-keyless-js).

### [Python](#tab/python)

Explore the Python [End to end Azure OpenAI Keyless Authentication Building Block AI template](https://github.com/Azure-Samples/azure-openai-keyless-python).

---

### Authenticate for local development

#### [.NET](#tab/csharp)

Select a tool for [authentication during local development](/dotnet/api/overview/azure/identity-readme#authenticate-the-client).

> [!IMPORTANT]
> For access to your Azure resources during local development, you must [sign-in to a local development tool](/dotnet/azure/sdk/authentication/local-development-dev-accounts#sign-in-to-azure-using-developer-tooling) using the Azure account you assigned the `Azure AI Developer` role to. For example, Visual Studio or the Azure CLI.

#### [Go](#tab/go)

Select a tool for [authentication during local development](https://github.com/Azure/azure-sdk-for-go/tree/main/sdk/azidentity#authenticating-during-local-development).

#### [Java](#tab/java)

Select a tool for [authentication during local development](/java/api/overview/azure/identity-readme#authenticate-the-client).

#### [JavaScript](#tab/javascript)

Select a tool for [authentication during local development](/javascript/api/overview/azure/identity-readme#authenticate-the-client-in-development-environment).

#### [Python](#tab/python)

Select a tool for [authentication during local development](/python/api/overview/azure/identity-readme#authenticate-during-local-development).

---

### Authenticate for Azure-hosted environments

#### [.NET](#tab/csharp)

Learn about how to manage the [DefaultAzureCredential](/dotnet/api/overview/azure/identity-readme#defaultazurecredential) for applications deployed to Azure.

#### [Go](#tab/go)

Learn about how to manage the [DefaultAzureCredential](https://pkg.go.dev/github.com/Azure/azure-sdk-for-go/sdk/azidentity#readme-defaultazurecredential) for applications deployed to Azure.

#### [Java](#tab/java)

Learn about how to manage the [DefaultAzureCredential](/java/api/overview/azure/identity-readme#defaultazurecredential) for applications deployed to Azure.

#### [JavaScript](#tab/javascript)

Learn about how to manage the [DefaultAzureCredential](/javascript/api/overview/azure/identity-readme#defaultazurecredential) for applications deployed to Azure.

#### [Python](#tab/python)

Learn about how to manage the [DefaultAzureCredential](/python/api/overview/azure/identity-readme#defaultazurecredential) for applications deployed to Azure.

---

## Configure roles for authorization

1. Find the [role](/azure/role-based-access-control/built-in-roles#ai--machine-learning) for your usage of Azure OpenAI. Depending on how you intend to set that role, you need either the name or ID.

   | Role name                                                 | Role ID                          |
   | --------------------------------------------------------- | -------------------------------- |
   | For Azure CLI or Azure PowerShell, you can use role name. | For Bicep, you need the role ID. |

1. Use the following table to select a role and ID.

   | Use case         | Role name                               | Role ID                                |
   | ---------------- | --------------------------------------- | -------------------------------------- |
   | Assistants       | `Cognitive Services OpenAI Contributor` | `a001fd3d-188f-4b5d-821b-7da978bf7442` |
   | Chat completions | `Cognitive Services OpenAI User`        | `5e0bd9bd-7b93-4f28-af87-19fc36ad61bd` |

1. Select an identity type to use.

   - **Personal identity**: This is your personal identity tied to your sign in to Azure.
   - **Managed identity**: This is an identity managed by and created for use on Azure. For [managed identity](/entra/identity/managed-identities-azure-resources/how-manage-user-assigned-managed-identities?pivots=identity-mi-methods-azp#create-a-user-assigned-managed-identity), create a [user-assigned managed identity](/entra/identity/managed-identities-azure-resources/how-manage-user-assigned-managed-identities?pivots=identity-mi-methods-azp#create-a-user-assigned-managed-identity). When you create the managed identity, you need the `Client ID`, also known as the `app ID`.

1. To find your personal identity, use one of the following commands. Use the ID as the `<identity-id>` in the next step.

   ### [Azure CLI](#tab/azure-cli)

   For local development, to get your own identity ID, use the following command. You need to sign in with `az login` before using this command.

   ```azurecli
   az ad signed-in-user show \
       --query id -o tsv
   ```

   ### [Azure PowerShell](#tab/azure-powershell)

   For local development, to get your own identity ID, use the following command. You need to sign in with `Connect-AzAccount` before using this command.

   ```azurepowershell
   (Get-AzContext).Account.ExtendedProperties.HomeAccountId.Split('.')[0]
   ```

   ### [Bicep](#tab/bicep)

   When using [Bicep](/azure/azure-resource-manager/bicep/) deployed with [Azure Developer CLI](/azure/developer/azure-developer-cli), the identity of the person or service running the deployment is set to the `principalId` parameter.

   The following `main.parameters.json` variable is set to the identity running the process.

   ```json
   "principalId": {
       "value": "${AZURE_PRINCIPAL_ID}"
     },
   ```

   For use in Azure, specify a user-assigned managed identity as part of the Bicep deployment process. Create a user-assigned managed identity separate from the identity running the process.

   ```bicep
   resource userAssignedManagedIdentity 'Microsoft.ManagedIdentity/userAssignedIdentities@2018-11-30' = {
     name: managedIdentityName
     location: location
   }
   ```

   ### [Azure portal](#tab/portal)

   Use the steps found here: [find the user object ID](/partner-center/find-ids-and-domain-names#find-the-user-object-id) in the Azure portal.

   ***

1. Assign the role-based access control (RBAC) role to the identity for the resource group.

   ### [Azure CLI](#tab/azure-cli)

   To grant your identity permissions to your resource through RBAC, assign a role using the Azure CLI command [az role assignment create](/cli/azure/role/assignment#az-role-assignment-create).

   ```azurecli
   az role assignment create \
       --role "Cognitive Services OpenAI User" \
       --assignee "<identity-id>" \
       --scope "/subscriptions/<subscription-id>/resourceGroups/<resource-group-name>"
   ```

   ### [Azure PowerShell](#tab/azure-powershell)

   To grant your application permissions to your Azure OpenAI resource through RBAC, assign a role using the Azure PowerShell cmdlet [New-AzRoleAssignment](/powershell/module/az.resources/new-azroleassignment).

   ```azurepowershell
   New-AzRoleAssignment -ObjectId "<identity-id>" -RoleDefinitionName "Cognitive Services OpenAI User" -Scope "/subscriptions/<subscription-id>/resourceGroups/<resource-group-name>"
   ```

   ### [Bicep](#tab/bicep)

   Use the following Azure OpenAI Bicep template to create the resource and set the authentication for the `identityId`. Bicep requires the role ID. The `name` shown in this Bicep snippet isn't the Azure role; it's specific to the Bicep deployment.

   ```bicep
   // main.bicep
   param environment string = 'production'

   // USER ROLES
   module openAiRoleUser 'core/security/role.bicep' = {
       scope: openAiResourceGroup
       name: 'openai-role-user'
       params: {
           principalId: (environment == 'development') ? principalId : userAssignedManagedIdentity
           principalType: (environment == 'development') ? 'User' : 'ServicePrincipal'
           roleDefinitionId: '5e0bd9bd-7b93-4f28-af87-19fc36ad61bd'
       }
   }
   ```

   The following generic Bicep is called from the `main.bicep` to create any role.

   ```bicep
   // core/security/role.bicep
   metadata description = 'Creates a role assignment for an identity.'
   param principalId string // passed in from main.bicep identityId

   @allowed([
       'Device'
       'ForeignGroup'
       'Group'
       'ServicePrincipal'
       'User'
   ])
   param principalType string = 'ServicePrincipal'
   param roleDefinitionId string

   resource role 'Microsoft.Authorization/roleAssignments@2022-04-01' = {
       name: guid(subscription().id, resourceGroup().id, principalId, roleDefinitionId)
       properties: {
           principalId: principalId
           principalType: principalType
           roleDefinitionId: resourceId('Microsoft.Authorization/roleDefinitions', roleDefinitionId)
       }
   }
   ```

   ### [Azure portal](#tab/portal)

   Use the steps found at [open the Add role assignment page](/azure/role-based-access-control/role-assignments-portal#step-2-open-the-add-role-assignment-page) in the Azure portal.

   ***

   Where applicable, replace `<identity-id>`, `<subscription-id>`, and `<resource-group-name>` with your actual values.

## Configure environment variables

To connect to Azure OpenAI, your code needs to know your resource endpoint, and _might_ need other environment variables.

1. Create an environment variable for your Azure OpenAI endpoint.

   - `AZURE_OPENAI_ENDPOINT`: This URL is the access point for your Azure OpenAI resource.

2. Create environment variables based on the location in which your app runs:

   | Location    | Identity                       | Description                                                                                                                               |
   | ----------- | ------------------------------ | ----------------------------------------------------------------------------------------------------------------------------------------- |
   | Local       | Personal                       | For local runtimes with your **personal identity**, [sign in](#authenticate-for-local-development) to create your credential with a tool. |
   | Azure cloud | User-assigned managed identity | Create an `AZURE_CLIENT_ID` environment variable containing the client ID of the user-assigned managed identity to authenticate as.       |

## Install Azure Identity client library

Use the following link to install the Azure Identity client library.

### [.NET](#tab/csharp)

Install the .NET [Azure Identity client library](https://www.nuget.org/packages/Azure.Identity):

```dotnetcli
dotnet add package Azure.Identity
```

### [Go](#tab/go)

Install the Go [Azure Identity client library](https://github.com/Azure/azure-sdk-for-go/tree/main/sdk/azidentity):

```bash
go get -u github.com/Azure/azure-sdk-for-go/sdk/azidentity
```

### [Java](#tab/java)

Install the Java [Azure Identity client library](https://mvnrepository.com/artifact/com.azure/azure-identity) with the following POM file:

```xml
<dependencyManagement>
    <dependencies>
        <dependency>
            <groupId>com.azure</groupId>
            <artifactId>azure-identity</artifactId>
            <version>1.10.0</version>
            <type>pom</type>
            <scope>import</scope>
        </dependency>
    </dependencies>
</dependencyManagement>
```

### [JavaScript](#tab/javascript)

Install the JavaScript [Azure Identity client library](https://www.npmjs.com/package/@azure/identity):

```console
npm install --save @azure/identity
```

### [Python](#tab/python)

Install the Python [Azure Identity client library](https://pypi.org/project/azure-identity/):

```console
pip install azure-identity
```

---

## Use DefaultAzureCredential

The Azure Identity library's `DefaultAzureCredential` allows the customer to run the same code in the local development environment and in the Azure Cloud.

### [.NET](#tab/csharp)

For more information on `DefaultAzureCredential` for .NET, see the [`DefaultAzureCredential` overview](/dotnet/azure/sdk/authentication/credential-chains?tabs=dac#defaultazurecredential-overview).

Take one of the following approaches to set the user-assigned managed identity's client ID:

- Set environment variable `AZURE_CLIENT_ID`. The parameterless constructor of `DefaultAzureCredential` uses the value of this environment variable, if present.

  ```csharp
  using Azure;
  using Azure.AI.OpenAI;
  using Azure.Identity;
  using System;
  using static System.Environment;

  string endpoint = GetEnvironmentVariable("AZURE_OPENAI_ENDPOINT");

  OpenAIClient client = new(new Uri(endpoint), new DefaultAzureCredential());
  ```

- Set property [ManagedIdentityClientId](/dotnet/api/azure.identity.defaultazurecredentialoptions.managedidentityclientid?view=azure-dotnet&preserve-view=true) on `DefaultAzureCredentialOptions`:

  ```csharp
  using Azure;
  using Azure.AI.OpenAI;
  using Azure.Identity;
  using System;
  using static System.Environment;

  string endpoint = GetEnvironmentVariable("AZURE_OPENAI_ENDPOINT");

  var credential = new DefaultAzureCredential(
      new DefaultAzureCredentialOptions
      {
          ManagedIdentityClientId = "<user_assigned_client_id>"
      });

  OpenAIClient client = new(new Uri(endpoint), credential);
  ```

### [Go](#tab/go)

For more information on `DefaultAzureCredential` for Go, see the [`DefaultAzureCredential` overview](/azure/developer/go/sdk/authentication/credential-chains#defaultazurecredential-overview).

```go
import (
	"log"

	"github.com/Azure/azure-sdk-for-go/sdk/ai/azopenai"
	"github.com/Azure/azure-sdk-for-go/sdk/azidentity"
)

func main() {
	dac, err := azidentity.NewDefaultAzureCredential(nil)

	if err != nil {
		log.Fatalf("ERROR: %s", err)
	}

	client, err := azopenai.NewClient(os.Getenv("AZURE_OPENAI_ENDPOINT"), dac, nil)

	if err != nil {
		log.Fatalf("ERROR: %s", err)
	}

	_ = client
}
```

### [Java](#tab/java)

For more information on `DefaultAzureCredential` for Java, see the [`DefaultAzureCredential` overview](/azure/developer/java/sdk/authentication/credential-chains#defaultazurecredential-overview).

Take one of the following approaches to set the user-assigned managed identity's client ID:

- Set environment variable `AZURE_CLIENT_ID`. The parameterless constructor of `DefaultAzureCredential` uses the value of this environment variable, if present.

  ```java
  import com.azure.identity.DefaultAzureCredentialBuilder;
  import com.azure.ai.openai.OpenAIClient;
  import com.azure.ai.openai.OpenAIClientBuilder;

  String endpoint = System.getenv("AZURE_OPENAI_ENDPOINT");

  DefaultAzureCredential credential = new DefaultAzureCredentialBuilder().build();
  OpenAIClient client = new OpenAIClientBuilder()
      .credential(credential)
      .endpoint(endpoint)
      .buildClient();
  ```

- Assign a specific user-assigned managed identity with `DefaultAzureCredential` by using the `DefaultAzureCredentialBuilder` to configure it with a client ID:

  ```java
  import com.azure.identity.DefaultAzureCredentialBuilder;
  import com.azure.ai.openai.OpenAIClient;
  import com.azure.ai.openai.OpenAIClientBuilder;

  String endpoint = System.getenv("AZURE_OPENAI_ENDPOINT");
  String userAssignedClientId = "<your managed identity client ID>";

  TokenCredential dacWithUserAssignedManagedIdentity
       = new DefaultAzureCredentialBuilder().managedIdentityClientId(userAssignedClientId).build();
  OpenAIClient client = new OpenAIClientBuilder()
      .credential(dacWithUserAssignedManagedIdentity)
      .endpoint(endpoint)
      .buildClient();
  ```

### [JavaScript](#tab/javascript)

For more information on `DefaultAzureCredential` for JavaScript, see the [`DefaultAzureCredential` overview](/azure/developer/javascript/sdk/authentication/credential-chains#use-defaultazurecredential-for-flexibility).

Take one of the following approaches to set the user-assigned managed identity's client ID:

- Set environment variable `AZURE_CLIENT_ID`. The parameterless constructor of `DefaultAzureCredential` uses the value of this environment variable, if present.

  ```javascript
  import {
    DefaultAzureCredential,
    getBearerTokenProvider,
  } from "@azure/identity";
  import { AzureOpenAI } from "openai";

  const credential = new DefaultAzureCredential();
  const scope = "https://cognitiveservices.azure.com/.default";
  const azureADTokenProvider = getBearerTokenProvider(credential, scope);

  const endpoint = process.env["AZURE_OPENAI_ENDPOINT"] || "<endpoint>";
  const deployment = "<your Azure OpenAI deployment name>";
  const apiVersion = "2024-05-01-preview";
  const options = { azureADTokenProvider, deployment, apiVersion, endpoint };

  const client = new AzureOpenAI(options);
  ```

- Assign a specific user-assigned managed identity with `DefaultAzureCredential` by using the `managedIdentityClientId` parameter to configure it with a client ID:

  ```javascript
  import {
    DefaultAzureCredential,
    getBearerTokenProvider,
  } from "@azure/identity";
  import { AzureOpenAI } from "openai";

  const managedIdentityClientId = "<your managed identity client ID>";

  const credential = new DefaultAzureCredential({
    managedIdentityClientId: managedIdentityClientId,
  });
  const scope = "https://cognitiveservices.azure.com/.default";
  const azureADTokenProvider = getBearerTokenProvider(credential, scope);

  const endpoint = process.env["AZURE_OPENAI_ENDPOINT"] || "<endpoint>";
  const deployment = "<your Azure OpenAI deployment name>";
  const apiVersion = "2024-05-01-preview";
  const options = { azureADTokenProvider, deployment, apiVersion, endpoint };

  const client = new AzureOpenAI(options);
  ```

### [Python](#tab/python)

For more information on `DefaultAzureCredential` for Python, see the [`DefaultAzureCredential` overview](/azure/developer/python/sdk/authentication/credential-chains?tabs=dac#defaultazurecredential-overview).

Take one of the following approaches to set the user-assigned managed identity's client ID:

- Set environment variable `AZURE_CLIENT_ID`. The parameterless constructor of `DefaultAzureCredential` uses the value of this environment variable, if present.

  ```python
  import openai
  from azure.identity import DefaultAzureCredential, get_bearer_token_provider

  token_provider = get_bearer_token_provider(DefaultAzureCredential(), "https://cognitiveservices.azure.com/.default")

  openai_client = openai.AzureOpenAI(
      api_version=os.getenv("AZURE_OPENAI_VERSION"),
      azure_endpoint=os.getenv("AZURE_OPENAI_ENDPOINT"),
      azure_ad_token_provider=token_provider
  )
  ```

- Assign a specific user-assigned managed identity with `DefaultAzureCredential` by using the `managed_identity_client_id` parameter to configure it with a client ID:

  ```python
  import openai
  from azure.identity import DefaultAzureCredential, get_bearer_token_provider

  user_assigned_client_id = "<your managed identity client ID>"

  credential = DefaultAzureCredential(
   managed_identity_client_id=user_assigned_client_id
  )

  token_provider = get_bearer_token_provider(credential, "https://cognitiveservices.azure.com/.default")

  openai_client = openai.AzureOpenAI(
      api_version=os.getenv("AZURE_OPENAI_VERSION"),
      azure_endpoint=os.getenv("AZURE_OPENAI_ENDPOINT"),
      azure_ad_token_provider=token_provider
  )

  ```

---

## Resources

- [Passwordless connections developer guide](/azure/developer/intro/passwordless-overview)
