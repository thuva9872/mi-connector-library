# ASB Connector Reference

The following configurations allow you to work with the ASB Connector.

## Overview

The [Azure Service Bus](https://docs.microsoft.com/en-us/azure/service-bus-messaging/) is a fully managed enterprise message broker with message queues and publish-subscribe topics. It
provides the capability to send and receive messages from Service Bus queues, topics, and subscriptions. The Azure
Service Bus handles messages that include data representing any kind of information, including structured data encoded
with common formats such as the following ones: JSON, XML, and Plain Text.

The [Ballerina](https://ballerina.io/) connector for Azure Service Bus allows you to connect to
an [Azure Service Bus](https://docs.microsoft.com/en-us/azure/service-bus-messaging/) via the Ballerina language.

This connector supports the following operations:
- Manage (Get/Create/Update/Delete/list) a queue, topic, subscription or rule.
- Send messages to a queue, topic, or subscription.
- Receive messages from a queue, topic, or subscription.

The Ballerina Azure Service Bus module utilizes Microsoft's [Azure Service Bus JAVA SDK 7.13.1](https://learn.microsoft.com/en-us/java/api/overview/azure/service-bus?view=azure-java-stable#libraries-for-data-access). 

## Setup guide

Before using this connector in your Ballerina application, complete the following:

### Create a namespace in the Azure portal

To begin using Service Bus messaging in Azure, you must first create a namespace with a name that is unique across Azure. A namespace provides a scoping container for Service Bus resources within your application.

To create a namespace:

#### Step 1: Sign in to the [Azure portal](https://portal.azure.com/)
If you don't have an Azure subscription, [sign up for a free Azure account](https://azure.microsoft.com/free/).

#### Step 2: Go to the Create Resource Service Bus menu

In the left navigation pane of the portal, select **All services**, select **Integration** from the list of categories, hover the mouse over **Service Bus**, and then select **Create** on the Service Bus tile.

![Create Resource Service Bus Menu](https://raw.githubusercontent.com/ballerina-platform/module-ballerinax-azure-service-bus/main/ballerina/resources/create-resource-service-bus-menu.png)

#### Step 3: In the Basics tag of the Create namespace page, follow these steps:

1. For **Subscription**, choose an Azure subscription in which to create the namespace.

2. For **Resource group**, choose an existing resource group in which the namespace will live, or create a new one.

3. Enter a **name for the namespace**. The namespace name should adhere to the following naming conventions:

* The name must be unique across Azure. The system immediately checks to see if the name is available.
* The name length is at least 6 and at most 50 characters.
* The name can contain only letters, numbers, and hyphens “-“.
* The name must start with a letter and end with a letter or number.
* The name doesn't end with “-sb“ or “-mgmt“.

4. For **Location**, choose the region in which your namespace should be hosted.

5. For **Pricing tier**, select the pricing tier (Basic, Standard, or Premium) for the namespace. For this quickstart, select Standard.

> **Notice:** If you want to use topics and subscriptions, choose either Standard or Premium. Topics/subscriptions aren't supported in the Basic pricing tier. If you selected the Premium pricing tier, specify the number of messaging units. The premium tier provides resource isolation at the CPU and memory level so that each workload runs in isolation. This resource container is called a messaging unit. A premium namespace has at least one messaging unit. You can select 1, 2, 4, 8, or 16 messaging units for each Service Bus Premium namespace. For more information, see [Service Bus Premium Messaging](https://learn.microsoft.com/en-us/azure/service-bus-messaging/service-bus-premium-messaging).`

6. Select **Review + create** at the bottom of the page.

![Create Namespace](https://raw.githubusercontent.com/ballerina-platform/module-ballerinax-azure-service-bus/main/ballerina/resources/create-namespace.png)

7. On the **Review + create** page, review settings, and select **Create**.


### Obtain tokens for authentication

To send and receive messages from a Service Bus queue or topic, clients must use a token that is signed by a shared access key, which is part of a shared access policy. A shared access policy defines a set of permissions that can be assigned to one or more Service Bus entities (queues, topics, event hubs, or relays). A shared access policy can be assigned to more than one entity, and a single entity can have more than one shared access policy assigned to it.

To obtain a token following steps should be followed:

1. In the left navigation pane of the portal, select *All services*, select *Integration* from the list of categories, hover the mouse over *Service Bus*, and then select your namespace.

2. In the left navigation pane of the namespace page, select *Shared access policies*.

3. Click on the *RootManageSharedAccessKey* policy.

4. Copy the *Primary Connection String* value and save it in a secure location. This is the connection string that you use to authenticate with the Service Bus service.

![Connection String](https://raw.githubusercontent.com/ballerina-platform/module-ballerinax-azure-service-bus/main/ballerina/resources/connection-string.png)


## Quickstart
To use the ASB connector in your Ballerina application, modify the .bal file as follows:

### Step 1: Import connector

Import the `ballerinax/asb` module into the Ballerina project.

```ballerina
import ballerinax/asb;
```

### Step 2: Create a new connector instance

#### Initialize an Admin Client

This can be done by providing a connection string.

````ballerina
    configurable string connectionString = ?;
    asb:AdminClient admin = check new (connectionString);
````

#### Initialize a Message Sender client

This can be done by providing a connection string with a queue or topic name.

```ballerina
    configurable string connectionString = ?;

    ASBServiceSenderConfig senderConfig = {
        connectionString: connectionString,
        entityType: QUEUE,
        topicOrQueueName: "myQueue"
    };
    asb:MessageSender sender = check new (senderConfig);
```

#### Initialize a Message Receiver client

This can be done by providing a connection string with a queue name, topic name, or subscription path. 

> Here, the Receive mode is optional. (Default: PEEKLOCK)

```ballerina
    configurable string connectionString = ?;

    ASBServiceReceiverConfig receiverConfig = {
        connectionString: connectionString,
        entityConfig: {
            queueName: "myQueue"
        },
        receiveMode: PEEK_LOCK
    };
    asb:MessageReceiver receiver = check new (receiverConfig);
```

#### Initialize a message listener

This can be done by providing a connection string with a queue name, topic name, or subscription path.

> Here, the Receive mode is optional. (Default: PEEKLOCK)

```ballerina
    configurable string connectionString = ?;

    listener asb:Listener asbListener = check new (
        connectionString = connectionString,
        entityConfig = {
            queueName: "myQueue"
        }
    );
```

### Step 3: Invoke connector operation

Now you can use the remote operations available within the connector,

**Create a queue in the Azure Service Bus**

 ```ballerina
public function main() returns error? {
    asb:AdminClient admin = check new (adminConfig);

    check admin->createQueue("myQueue");

    check admin->close();
}
 ```

**Send a message to the Azure Service Bus**

```ballerina
public function main() returns error? {
    asb:MessageSender queueSender = check new (senderConfig);

    string stringContent = "This is My Message Body"; 
    byte[] byteContent = stringContent.toBytes();
    int timeToLive = 60; // In seconds

    asb:ApplicationProperties applicationProperties = {
        properties: {a: "propertyValue1", b: "propertyValue2"}
    };

    asb:Message message = {
        body: byteContent,
        contentType: asb:TEXT,
        timeToLive: timeToLive,
        applicationProperties: applicationProperties
    };

    check queueSender->send(message);

    check queueSender->close();
}
```

**Receive a message from the Azure Service Bus**

```ballerina
public function main() returns error? {
    asb:MessageReceiver queueReceiver = check new (receiverConfig);

    int serverWaitTime = 60; // In seconds

    asb:Message|asb:Error? messageReceived = queueReceiver->receive(serverWaitTime);

    if (messageReceived is asb:Message) {
        log:printInfo("Reading Received Message : " + messageReceived.toString());
    } else if (messageReceived is ()) {
        log:printError("No message in the queue.");
    } else {
        log:printError("Receiving message via Asb receiver connection failed.");
    }

    check queueReceiver->close();
}
```

**Receive messages from Azure service bus using `asb:Service`**

```ballerina
service asb:Service on asbListener {

    isolated remote function onMessage(asb:Message message) returns error? {
        log:printInfo("Reading Received Message : " + message.toString());
    }

    isolated remote function onError(asb:MessageRetrievalError 'error) returns error? {
        log:printError("Error occurred while receiving messages from ASB", 'error);
    }
}
```

### Step 4: Run the Ballerina application

```bash
bal run
```

## Examples

There are two sets of examples demonstrating the use of the Ballerina Azure Service Bus (ASB) Connector.

- **[Management Related Examples](https://github.com/ballerina-platform/module-ballerinax-azure-service-bus/tree/main/examples/admin)**: These examples cover operations related to managing the Service Bus, such as managing queues, topics, subscriptions, and rules. 

- **[Message Sending and Receiving Related Examples](https://github.com/ballerina-platform/module-ballerinax-azure-service-bus/tree/main/examples/sender_reciever)**: This set includes examples for sending to and receiving messages from queues, topics, and subscriptions in the Service Bus.


## Connection Configurations

The following connection types are available:

??? note "Connection Config for asb_Administrator connection"
    asb_Administrator Connection Ballerina Service Bus connector provides the capability to access Azure Service Bus SDK.
    Service Bus API provides data access to highly reliable queues and publish/subscribe topics of Azure Service Bus with deep feature capabilities.

    <table>
    <tr>
    <th>Parameter Name</th>
    <th>Element</th>
    <th>Type</th>
    <th>Description</th>
    <th>Default Value</th>
    <th>Required</th>
    </tr>
    <tr>
    <td>Connection Name</td>
    <td>connectionName</td>
    <td>String</td>
    <td>The name for the asb_Administrator connection</td>
    <td>asb_Administrator_connection_1</td>
    <td>Yes</td>
    </tr>
    <tr>
    <td>connectionString<br/><small>(Basic)</small></td>
    <td>connectionString</td>
    <td>String</td>
    <td>Service bus connection string with Shared Access Signatures  
    ConnectionString format:
    Endpoint=sb://namespace_DNS_Name;EntityPath=EVENT_HUB_NAME;
    SharedAccessKeyName=SHARED_ACCESS_KEY_NAME;SharedAccessKey=SHARED_ACCESS_KEY or
    Endpoint=sb://namespace_DNS_Name;EntityPath=EVENT_HUB_NAME;
    SharedAccessSignatureToken=SHARED_ACCESS_SIGNATURE_TOKEN</td>
    <td>-</td>
    <td>Yes</td>
    </tr>
    </table>

    **Sample configuration**
    ```xml
    <asb.init>
        <connectionType>asb_Administrator</connectionType>
        <connectionString>{$ctx:connectionString}</connectionString>
    </asb.init>
    ```

??? note "Connection Config for asb_MessageReceiver connection"
    asb_MessageReceiver Connection Ballerina Service Bus connector provides the capability to access Azure Service Bus SDK.
    Service Bus API provides data access to highly reliable queues and publish/subscribe topics of Azure Service Bus with deep feature capabilities.

    <table>
    <tr>
    <th>Parameter Name</th>
    <th>Element</th>
    <th>Type</th>
    <th>Description</th>
    <th>Default Value</th>
    <th>Required</th>
    </tr>
    <tr>
    <td>Connection Name</td>
    <td>connectionName</td>
    <td>String</td>
    <td>The name for the asb_MessageReceiver connection</td>
    <td>asb_MessageReceiver_connection_1</td>
    <td>Yes</td>
    </tr>
    <tr>
    <td>connectionString<br/><small>(Basic)</small></td>
    <td>connectionString</td>
    <td>String</td>
    <td>Service bus connection string with Shared Access Signatures  
    ConnectionString format:
    Endpoint=sb://namespace_DNS_Name;EntityPath=EVENT_HUB_NAME;
    SharedAccessKeyName=SHARED_ACCESS_KEY_NAME;SharedAccessKey=SHARED_ACCESS_KEY or
    Endpoint=sb://namespace_DNS_Name;EntityPath=EVENT_HUB_NAME;
    SharedAccessSignatureToken=SHARED_ACCESS_SIGNATURE_TOKEN</td>
    <td>-</td>
    <td>Yes</td>
    </tr>
    <tr>
    <td>entityConfigDataType<br/><small>(Basic)</small></td>
    <td>entityConfigDataType</td>
    <td>Enum</td>
    <td><b>Possible values</b>: <code>TopicSubsConfig</code>, <code>QueueConfig</code></td>
    <td>TopicSubsConfig</td>
    <td>Yes</td>
    </tr>
    <tr>
    <td>topicName<br/><small>(Basic > Entity Config)</small></td>
    <td>entityConfig_topicName</td>
    <td>String</td>
    <td>-</td>
    <td>-</td>
    <td>Yes</td>
    </tr>
    <tr>
    <td>subscriptionName<br/><small>(Basic > Entity Config)</small></td>
    <td>entityConfig_subscriptionName</td>
    <td>String</td>
    <td>-</td>
    <td>-</td>
    <td>Yes</td>
    </tr>
    <tr>
    <td>queueName<br/><small>(Basic > Entity Config)</small></td>
    <td>entityConfig_queueName</td>
    <td>String</td>
    <td>-</td>
    <td>-</td>
    <td>Yes</td>
    </tr>
    <tr>
    <td>receiveMode<br/><small>(Basic)</small></td>
    <td>receiveMode</td>
    <td>Enum</td>
    <td>This field holds the receive modes(RECEIVE_AND_DELETE/PEEK_LOCK) for the connection. The receive mode determines how messages are 
    retrieved from the entity. The default value is PEEK_LOCK<br/><b>Possible values</b>: <code>PEEK_LOCK</code>, <code>RECEIVE_AND_DELETE</code></td>
    <td>PEEK_LOCK</td>
    <td>No</td>
    </tr>
    <tr>
    <td>maxAutoLockRenewDuration<br/><small>(Basic)</small></td>
    <td>maxAutoLockRenewDuration</td>
    <td>String</td>
    <td>Max lock renewal duration under PEEK_LOCK mode in seconds. Setting to 0 disables auto-renewal. 
    For RECEIVE_AND_DELETE mode, auto-renewal is disabled. Default 300 seconds.</td>
    <td>-</td>
    <td>No</td>
    </tr>
    <tr>
    <td>Configure amqpRetryOptions<br/><small>(Basic)</small></td>
    <td>enable_amqpRetryOptions</td>
    <td>Boolean</td>
    <td>Enable to configure amqpRetryOptions settings</td>
    <td>false</td>
    <td>No</td>
    </tr>
    <tr>
    <td>maxRetries<br/><small>(Basic > Amqp Retry Options)</small></td>
    <td>amqpRetryOptions.maxRetries</td>
    <td>String</td>
    <td>Maximum number of retry attempts</td>
    <td>-</td>
    <td>No</td>
    </tr>
    <tr>
    <td>delay<br/><small>(Basic > Amqp Retry Options)</small></td>
    <td>amqpRetryOptions.delay</td>
    <td>String</td>
    <td>Delay between retry attempts in seconds</td>
    <td>-</td>
    <td>No</td>
    </tr>
    <tr>
    <td>maxDelay<br/><small>(Basic > Amqp Retry Options)</small></td>
    <td>amqpRetryOptions.maxDelay</td>
    <td>String</td>
    <td>Maximum permissible delay between retry attempts in seconds</td>
    <td>-</td>
    <td>No</td>
    </tr>
    <tr>
    <td>tryTimeout<br/><small>(Basic > Amqp Retry Options)</small></td>
    <td>amqpRetryOptions.tryTimeout</td>
    <td>String</td>
    <td>Maximum duration to wait for completion of a single attempt in seconds</td>
    <td>-</td>
    <td>No</td>
    </tr>
    <tr>
    <td>retryMode<br/><small>(Basic > Amqp Retry Options)</small></td>
    <td>amqpRetryOptions_retryMode</td>
    <td>Enum</td>
    <td><b>Possible values</b>: <code>EXPONENTIAL</code>, <code>FIXED</code></td>
    <td>EXPONENTIAL</td>
    <td>No</td>
    </tr>
    </table>

    **Sample configuration**
    ```xml
    <asb.init>
        <connectionType>asb_MessageReceiver</connectionType>
        <connectionString>{$ctx:connectionString}</connectionString>
        <entityConfigDataType>{$ctx:entityConfigDataType}</entityConfigDataType>
        <entityConfig_topicName>{$ctx:entityConfig_topicName}</entityConfig_topicName>
        <entityConfig_subscriptionName>{$ctx:entityConfig_subscriptionName}</entityConfig_subscriptionName>
        <entityConfig_queueName>{$ctx:entityConfig_queueName}</entityConfig_queueName>
    </asb.init>
    ```

??? note "Connection Config for asb_MessageSender connection"
    asb_MessageSender Connection Ballerina Service Bus connector provides the capability to access Azure Service Bus SDK.
    Service Bus API provides data access to highly reliable queues and publish/subscribe topics of Azure Service Bus with deep feature capabilities.

    <table>
    <tr>
    <th>Parameter Name</th>
    <th>Element</th>
    <th>Type</th>
    <th>Description</th>
    <th>Default Value</th>
    <th>Required</th>
    </tr>
    <tr>
    <td>Connection Name</td>
    <td>connectionName</td>
    <td>String</td>
    <td>The name for the asb_MessageSender connection</td>
    <td>asb_MessageSender_connection_1</td>
    <td>Yes</td>
    </tr>
    <tr>
    <td>entityType<br/><small>(Basic)</small></td>
    <td>entityType</td>
    <td>Enum</td>
    <td>An enumeration value of type EntityType, which specifies whether the connection is for a topic or a queue. 
    The valid values are TOPIC and QUEUE<br/><b>Possible values</b>: <code>topic</code>, <code>queue</code></td>
    <td>topic</td>
    <td>Yes</td>
    </tr>
    <tr>
    <td>topicOrQueueName<br/><small>(Basic)</small></td>
    <td>topicOrQueueName</td>
    <td>String</td>
    <td>A string field that holds the name of the topic or queue</td>
    <td>-</td>
    <td>Yes</td>
    </tr>
    <tr>
    <td>connectionString<br/><small>(Basic)</small></td>
    <td>connectionString</td>
    <td>String</td>
    <td>Service bus connection string with Shared Access Signatures  
    ConnectionString format:
    Endpoint=sb://namespace_DNS_Name;EntityPath=EVENT_HUB_NAME;
    SharedAccessKeyName=SHARED_ACCESS_KEY_NAME;SharedAccessKey=SHARED_ACCESS_KEY or
    Endpoint=sb://namespace_DNS_Name;EntityPath=EVENT_HUB_NAME;
    SharedAccessSignatureToken=SHARED_ACCESS_SIGNATURE_TOKEN</td>
    <td>-</td>
    <td>Yes</td>
    </tr>
    <tr>
    <td>Configure amqpRetryOptions<br/><small>(Basic)</small></td>
    <td>enable_amqpRetryOptions</td>
    <td>Boolean</td>
    <td>Enable to configure amqpRetryOptions settings</td>
    <td>false</td>
    <td>No</td>
    </tr>
    <tr>
    <td>maxRetries<br/><small>(Basic > Amqp Retry Options)</small></td>
    <td>amqpRetryOptions.maxRetries</td>
    <td>String</td>
    <td>Maximum number of retry attempts</td>
    <td>-</td>
    <td>No</td>
    </tr>
    <tr>
    <td>delay<br/><small>(Basic > Amqp Retry Options)</small></td>
    <td>amqpRetryOptions.delay</td>
    <td>String</td>
    <td>Delay between retry attempts in seconds</td>
    <td>-</td>
    <td>No</td>
    </tr>
    <tr>
    <td>maxDelay<br/><small>(Basic > Amqp Retry Options)</small></td>
    <td>amqpRetryOptions.maxDelay</td>
    <td>String</td>
    <td>Maximum permissible delay between retry attempts in seconds</td>
    <td>-</td>
    <td>No</td>
    </tr>
    <tr>
    <td>tryTimeout<br/><small>(Basic > Amqp Retry Options)</small></td>
    <td>amqpRetryOptions.tryTimeout</td>
    <td>String</td>
    <td>Maximum duration to wait for completion of a single attempt in seconds</td>
    <td>-</td>
    <td>No</td>
    </tr>
    <tr>
    <td>retryMode<br/><small>(Basic > Amqp Retry Options)</small></td>
    <td>amqpRetryOptions_retryMode</td>
    <td>Enum</td>
    <td><b>Possible values</b>: <code>EXPONENTIAL</code>, <code>FIXED</code></td>
    <td>EXPONENTIAL</td>
    <td>No</td>
    </tr>
    </table>

    **Sample configuration**
    ```xml
    <asb.init>
        <connectionType>asb_MessageSender</connectionType>
        <entityType>{$ctx:entityType}</entityType>
        <topicOrQueueName>{$ctx:topicOrQueueName}</topicOrQueueName>
        <connectionString>{$ctx:connectionString}</connectionString>
    </asb.init>
    ```

## Operations

The following operations allow you to work with the ASB Connector. Click an operation name to see parameter details and samples on how to use it.

### Administrator

??? note "create queue"
    Create a queue with the given name or name and options.
    ```ballerina
    asb:QueueProperties queueProperties = check admin->createQueue("queue-1");
    ```

    <table>
    <tr>
    <th>Parameter Name</th>
    <th>Element</th>
    <th>Type</th>
    <th>Description</th>
    <th>Default Value</th>
    <th>Required</th>
    </tr>
    <tr>
    <td>queueName</td>
    <td>queueName</td>
    <td>String</td>
    <td>Name of the queue</td>
    <td>-</td>
    <td>Yes</td>
    </tr>
    <tr>
    <td>seconds<br/><small>(Auto Delete On Idle)</small></td>
    <td>autoDeleteOnIdle.seconds</td>
    <td>String</td>
    <td>Seconds</td>
    <td>-</td>
    <td>No</td>
    </tr>
    <tr>
    <td>nanoseconds<br/><small>(Auto Delete On Idle)</small></td>
    <td>autoDeleteOnIdle.nanoseconds</td>
    <td>String</td>
    <td>Nanoseconds</td>
    <td>-</td>
    <td>No</td>
    </tr>
    <tr>
    <td>seconds<br/><small>(Default Message Time To Live)</small></td>
    <td>defaultMessageTimeToLive.seconds</td>
    <td>String</td>
    <td>Seconds</td>
    <td>-</td>
    <td>No</td>
    </tr>
    <tr>
    <td>nanoseconds<br/><small>(Default Message Time To Live)</small></td>
    <td>defaultMessageTimeToLive.nanoseconds</td>
    <td>String</td>
    <td>Nanoseconds</td>
    <td>-</td>
    <td>No</td>
    </tr>
    <tr>
    <td>seconds<br/><small>(Duplicate Detection History Time Window)</small></td>
    <td>duplicateDetectionHistoryTimeWindow.seconds</td>
    <td>String</td>
    <td>Seconds</td>
    <td>-</td>
    <td>No</td>
    </tr>
    <tr>
    <td>nanoseconds<br/><small>(Duplicate Detection History Time Window)</small></td>
    <td>duplicateDetectionHistoryTimeWindow.nanoseconds</td>
    <td>String</td>
    <td>Nanoseconds</td>
    <td>-</td>
    <td>No</td>
    </tr>
    <tr>
    <td>forwardDeadLetteredMessagesTo</td>
    <td>forwardDeadLetteredMessagesTo</td>
    <td>String</td>
    <td>The name of the recipient entity to which all the dead-lettered messages of this subscription are forwarded to.</td>
    <td>-</td>
    <td>No</td>
    </tr>
    <tr>
    <td>forwardTo</td>
    <td>forwardTo</td>
    <td>String</td>
    <td>The name of the recipient entity to which all the messages sent to the queue are forwarded to</td>
    <td>-</td>
    <td>No</td>
    </tr>
    <tr>
    <td>seconds<br/><small>(Lock Duration)</small></td>
    <td>lockDuration.seconds</td>
    <td>String</td>
    <td>Seconds</td>
    <td>-</td>
    <td>No</td>
    </tr>
    <tr>
    <td>nanoseconds<br/><small>(Lock Duration)</small></td>
    <td>lockDuration.nanoseconds</td>
    <td>String</td>
    <td>Nanoseconds</td>
    <td>-</td>
    <td>No</td>
    </tr>
    <tr>
    <td>maxDeliveryCount</td>
    <td>maxDeliveryCount</td>
    <td>String</td>
    <td>The maximum delivery count. A message is automatically deadlettered after this number of deliveries. Default value is 10.</td>
    <td>-</td>
    <td>No</td>
    </tr>
    <tr>
    <td>maxMessageSizeInKilobytes</td>
    <td>maxMessageSizeInKilobytes</td>
    <td>String</td>
    <td>The maximum size of the queue in megabytes, which is the size of memory allocated for the queue</td>
    <td>-</td>
    <td>No</td>
    </tr>
    <tr>
    <td>maxSizeInMegabytes</td>
    <td>maxSizeInMegabytes</td>
    <td>String</td>
    <td>The maximum size of the queue in megabytes, which is the size of memory allocated for the queue</td>
    <td>-</td>
    <td>No</td>
    </tr>
    <tr>
    <td>status</td>
    <td>status</td>
    <td>Enum</td>
    <td>Enumerates the possible values for the status of a messaging entity<br/><b>Possible values</b>: <code>Unknown</code>, <code>SendDisabled</code>, <code>Restoring</code>, <code>Renaming</code>, <code>ReceiveDisabled</code>, <code>Disabled</code>, <code>Deleting</code>, <code>Creating</code>, <code>Active</code></td>
    <td>Unknown</td>
    <td>No</td>
    </tr>
    <tr>
    <td>userMetadata</td>
    <td>userMetadata</td>
    <td>String</td>
    <td>Metadata associated with the queue</td>
    <td>-</td>
    <td>No</td>
    </tr>
    <tr>
    <td>enableBatchedOperations</td>
    <td>enableBatchedOperations</td>
    <td>Boolean</td>
    <td>Value that indicates whether server-side batched operations are enabled</td>
    <td>-</td>
    <td>No</td>
    </tr>
    <tr>
    <td>deadLetteringOnMessageExpiration</td>
    <td>deadLetteringOnMessageExpiration</td>
    <td>Boolean</td>
    <td>Value that indicates whether this queue has dead letter support when a message expires</td>
    <td>-</td>
    <td>No</td>
    </tr>
    <tr>
    <td>requiresDuplicateDetection</td>
    <td>requiresDuplicateDetection</td>
    <td>Boolean</td>
    <td>Value indicating if this queue requires duplicate detection</td>
    <td>-</td>
    <td>No</td>
    </tr>
    <tr>
    <td>enablePartitioning</td>
    <td>enablePartitioning</td>
    <td>Boolean</td>
    <td>Value that indicates whether the queue is to be partitioned across multiple message brokers</td>
    <td>-</td>
    <td>No</td>
    </tr>
    <tr>
    <td>requiresSession</td>
    <td>requiresSession</td>
    <td>Boolean</td>
    <td>Value that indicates whether the queue supports the concept of sessions</td>
    <td>-</td>
    <td>No</td>
    </tr>
    <tr>
    <td>Output Variable Name</td>
    <td>responseVariable</td>
    <td>String</td>
    <td>The target variable in which the output of the operation will be stored</td>
    <td>-</td>
    <td>No</td>
    </tr>
    <tr>
    <td>Overwrite Message Body</td>
    <td>overwriteBody</td>
    <td>Boolean</td>
    <td>Replace the Message Body in Message Context with the output payload of the operation (This will remove the payload from the above variable. But other elements such as headers and attributes will remain).</td>
    <td>false</td>
    <td>No</td>
    </tr>
    </table>

    **Sample configuration**
    ```xml
    <asb.Administrator_createQueue configKey="CONNECTION_NAME">
        <queueName>{$ctx:queueName}</queueName>
        <status>{$ctx:status}</status>
        <responseVariable>asb_Administrator_createQueue_1</responseVariable>
        <overwriteBody>false</overwriteBody>
    </asb.Administrator_createQueue>
    ```

??? note "create rule"
    Create a rule with the given name or name and options.
    ```ballerina
    asb:RuleProperties? properties = check admin->createRule("topic-1", "sub-a", "rule-1");
    ```

    <table>
    <tr>
    <th>Parameter Name</th>
    <th>Element</th>
    <th>Type</th>
    <th>Description</th>
    <th>Default Value</th>
    <th>Required</th>
    </tr>
    <tr>
    <td>topicName</td>
    <td>topicName</td>
    <td>String</td>
    <td>Name of the topic associated with subscription</td>
    <td>-</td>
    <td>Yes</td>
    </tr>
    <tr>
    <td>subscriptionName</td>
    <td>subscriptionName</td>
    <td>String</td>
    <td>Name of the subscription</td>
    <td>-</td>
    <td>Yes</td>
    </tr>
    <tr>
    <td>ruleName</td>
    <td>ruleName</td>
    <td>String</td>
    <td>Name of the rule</td>
    <td>-</td>
    <td>Yes</td>
    </tr>
    <tr>
    <td>filter<br/><small>(Rule)</small></td>
    <td>rule_filter</td>
    <td>String</td>
    <td>-</td>
    <td>-</td>
    <td>No</td>
    </tr>
    <tr>
    <td>action<br/><small>(Rule)</small></td>
    <td>rule_action</td>
    <td>String</td>
    <td>-</td>
    <td>-</td>
    <td>No</td>
    </tr>
    <tr>
    <td>Output Variable Name</td>
    <td>responseVariable</td>
    <td>String</td>
    <td>The target variable in which the output of the operation will be stored</td>
    <td>-</td>
    <td>No</td>
    </tr>
    <tr>
    <td>Overwrite Message Body</td>
    <td>overwriteBody</td>
    <td>Boolean</td>
    <td>Replace the Message Body in Message Context with the output payload of the operation (This will remove the payload from the above variable. But other elements such as headers and attributes will remain).</td>
    <td>false</td>
    <td>No</td>
    </tr>
    </table>

    **Sample configuration**
    ```xml
    <asb.Administrator_createRule configKey="CONNECTION_NAME">
        <topicName>{$ctx:topicName}</topicName>
        <subscriptionName>{$ctx:subscriptionName}</subscriptionName>
        <ruleName>{$ctx:ruleName}</ruleName>
        <responseVariable>asb_Administrator_createRule_1</responseVariable>
        <overwriteBody>false</overwriteBody>
    </asb.Administrator_createRule>
    ```

??? note "create subscription"
    Create a subscription with the given name or name and options.
    ```ballerina
    asb:SubscriptionProperties? subscriptionProperties = check admin->createSubscription("topic-1", "sub-a");
    ```

    <table>
    <tr>
    <th>Parameter Name</th>
    <th>Element</th>
    <th>Type</th>
    <th>Description</th>
    <th>Default Value</th>
    <th>Required</th>
    </tr>
    <tr>
    <td>topicName</td>
    <td>topicName</td>
    <td>String</td>
    <td>Name of the topic associated with subscription</td>
    <td>-</td>
    <td>Yes</td>
    </tr>
    <tr>
    <td>subscriptionName</td>
    <td>subscriptionName</td>
    <td>String</td>
    <td>Name of the subscription</td>
    <td>-</td>
    <td>Yes</td>
    </tr>
    <tr>
    <td>seconds<br/><small>(Auto Delete On Idle)</small></td>
    <td>autoDeleteOnIdle.seconds</td>
    <td>String</td>
    <td>Seconds</td>
    <td>-</td>
    <td>No</td>
    </tr>
    <tr>
    <td>nanoseconds<br/><small>(Auto Delete On Idle)</small></td>
    <td>autoDeleteOnIdle.nanoseconds</td>
    <td>String</td>
    <td>Nanoseconds</td>
    <td>-</td>
    <td>No</td>
    </tr>
    <tr>
    <td>enableBatchedOperations</td>
    <td>enableBatchedOperations</td>
    <td>Boolean</td>
    <td>Value that indicates whether server-side batched operations are enabled</td>
    <td>-</td>
    <td>No</td>
    </tr>
    <tr>
    <td>deadLetteringOnMessageExpiration</td>
    <td>deadLetteringOnMessageExpiration</td>
    <td>Boolean</td>
    <td>Value that indicates whether this queue has dead letter support when a message expires</td>
    <td>-</td>
    <td>No</td>
    </tr>
    <tr>
    <td>seconds<br/><small>(Default Message Time To Live)</small></td>
    <td>defaultMessageTimeToLive.seconds</td>
    <td>String</td>
    <td>Seconds</td>
    <td>-</td>
    <td>No</td>
    </tr>
    <tr>
    <td>nanoseconds<br/><small>(Default Message Time To Live)</small></td>
    <td>defaultMessageTimeToLive.nanoseconds</td>
    <td>String</td>
    <td>Nanoseconds</td>
    <td>-</td>
    <td>No</td>
    </tr>
    <tr>
    <td>deadLetteringOnFilterEvaluationExceptions</td>
    <td>deadLetteringOnFilterEvaluationExceptions</td>
    <td>Boolean</td>
    <td>Value that indicates whether this subscription has dead letter support when a message expires</td>
    <td>-</td>
    <td>No</td>
    </tr>
    <tr>
    <td>forwardDeadLetteredMessagesTo</td>
    <td>forwardDeadLetteredMessagesTo</td>
    <td>String</td>
    <td>The name of the recipient entity to which all the dead-lettered messages of this subscription are forwarded to.</td>
    <td>-</td>
    <td>No</td>
    </tr>
    <tr>
    <td>forwardTo</td>
    <td>forwardTo</td>
    <td>String</td>
    <td>The name of the recipient entity to which all the messages sent to the queue are forwarded to</td>
    <td>-</td>
    <td>No</td>
    </tr>
    <tr>
    <td>seconds<br/><small>(Lock Duration)</small></td>
    <td>lockDuration.seconds</td>
    <td>String</td>
    <td>Seconds</td>
    <td>-</td>
    <td>No</td>
    </tr>
    <tr>
    <td>nanoseconds<br/><small>(Lock Duration)</small></td>
    <td>lockDuration.nanoseconds</td>
    <td>String</td>
    <td>Nanoseconds</td>
    <td>-</td>
    <td>No</td>
    </tr>
    <tr>
    <td>maxDeliveryCount</td>
    <td>maxDeliveryCount</td>
    <td>String</td>
    <td>The maximum delivery count. A message is automatically deadlettered after this number of deliveries. Default value is 10.</td>
    <td>-</td>
    <td>No</td>
    </tr>
    <tr>
    <td>requiresSession</td>
    <td>requiresSession</td>
    <td>Boolean</td>
    <td>Value that indicates whether the queue supports the concept of sessions</td>
    <td>-</td>
    <td>No</td>
    </tr>
    <tr>
    <td>status</td>
    <td>status</td>
    <td>Enum</td>
    <td>Enumerates the possible values for the status of a messaging entity<br/><b>Possible values</b>: <code>Unknown</code>, <code>SendDisabled</code>, <code>Restoring</code>, <code>Renaming</code>, <code>ReceiveDisabled</code>, <code>Disabled</code>, <code>Deleting</code>, <code>Creating</code>, <code>Active</code></td>
    <td>Unknown</td>
    <td>No</td>
    </tr>
    <tr>
    <td>userMetadata</td>
    <td>userMetadata</td>
    <td>String</td>
    <td>Metadata associated with the queue</td>
    <td>-</td>
    <td>No</td>
    </tr>
    <tr>
    <td>Output Variable Name</td>
    <td>responseVariable</td>
    <td>String</td>
    <td>The target variable in which the output of the operation will be stored</td>
    <td>-</td>
    <td>No</td>
    </tr>
    <tr>
    <td>Overwrite Message Body</td>
    <td>overwriteBody</td>
    <td>Boolean</td>
    <td>Replace the Message Body in Message Context with the output payload of the operation (This will remove the payload from the above variable. But other elements such as headers and attributes will remain).</td>
    <td>false</td>
    <td>No</td>
    </tr>
    </table>

    **Sample configuration**
    ```xml
    <asb.Administrator_createSubscription configKey="CONNECTION_NAME">
        <topicName>{$ctx:topicName}</topicName>
        <subscriptionName>{$ctx:subscriptionName}</subscriptionName>
        <status>{$ctx:status}</status>
        <responseVariable>asb_Administrator_createSubscription_1</responseVariable>
        <overwriteBody>false</overwriteBody>
    </asb.Administrator_createSubscription>
    ```

??? note "create topic"
    Create a topic with the given name or name and options.
    ```ballerina
    asb:TopicProperties? topicProperties = check admin->createTopic("topic-1");
    ```

    <table>
    <tr>
    <th>Parameter Name</th>
    <th>Element</th>
    <th>Type</th>
    <th>Description</th>
    <th>Default Value</th>
    <th>Required</th>
    </tr>
    <tr>
    <td>topicName</td>
    <td>topicName</td>
    <td>String</td>
    <td>Topic name</td>
    <td>-</td>
    <td>Yes</td>
    </tr>
    <tr>
    <td>seconds<br/><small>(Auto Delete On Idle)</small></td>
    <td>autoDeleteOnIdle.seconds</td>
    <td>String</td>
    <td>Seconds</td>
    <td>-</td>
    <td>No</td>
    </tr>
    <tr>
    <td>nanoseconds<br/><small>(Auto Delete On Idle)</small></td>
    <td>autoDeleteOnIdle.nanoseconds</td>
    <td>String</td>
    <td>Nanoseconds</td>
    <td>-</td>
    <td>No</td>
    </tr>
    <tr>
    <td>seconds<br/><small>(Default Message Time To Live)</small></td>
    <td>defaultMessageTimeToLive.seconds</td>
    <td>String</td>
    <td>Seconds</td>
    <td>-</td>
    <td>No</td>
    </tr>
    <tr>
    <td>nanoseconds<br/><small>(Default Message Time To Live)</small></td>
    <td>defaultMessageTimeToLive.nanoseconds</td>
    <td>String</td>
    <td>Nanoseconds</td>
    <td>-</td>
    <td>No</td>
    </tr>
    <tr>
    <td>seconds<br/><small>(Duplicate Detection History Time Window)</small></td>
    <td>duplicateDetectionHistoryTimeWindow.seconds</td>
    <td>String</td>
    <td>Seconds</td>
    <td>-</td>
    <td>No</td>
    </tr>
    <tr>
    <td>nanoseconds<br/><small>(Duplicate Detection History Time Window)</small></td>
    <td>duplicateDetectionHistoryTimeWindow.nanoseconds</td>
    <td>String</td>
    <td>Nanoseconds</td>
    <td>-</td>
    <td>No</td>
    </tr>
    <tr>
    <td>seconds<br/><small>(Lock Duration)</small></td>
    <td>lockDuration.seconds</td>
    <td>String</td>
    <td>Seconds</td>
    <td>-</td>
    <td>No</td>
    </tr>
    <tr>
    <td>nanoseconds<br/><small>(Lock Duration)</small></td>
    <td>lockDuration.nanoseconds</td>
    <td>String</td>
    <td>Nanoseconds</td>
    <td>-</td>
    <td>No</td>
    </tr>
    <tr>
    <td>maxDeliveryCount</td>
    <td>maxDeliveryCount</td>
    <td>String</td>
    <td>The maximum delivery count. A message is automatically deadlettered after this number of deliveries. Default value is 10.</td>
    <td>-</td>
    <td>No</td>
    </tr>
    <tr>
    <td>maxMessageSizeInKilobytes</td>
    <td>maxMessageSizeInKilobytes</td>
    <td>String</td>
    <td>The maximum size of the queue in megabytes, which is the size of memory allocated for the queue</td>
    <td>-</td>
    <td>No</td>
    </tr>
    <tr>
    <td>maxSizeInMegabytes</td>
    <td>maxSizeInMegabytes</td>
    <td>String</td>
    <td>The maximum size of the queue in megabytes, which is the size of memory allocated for the queue</td>
    <td>-</td>
    <td>No</td>
    </tr>
    <tr>
    <td>status</td>
    <td>status</td>
    <td>Enum</td>
    <td>Enumerates the possible values for the status of a messaging entity<br/><b>Possible values</b>: <code>Unknown</code>, <code>SendDisabled</code>, <code>Restoring</code>, <code>Renaming</code>, <code>ReceiveDisabled</code>, <code>Disabled</code>, <code>Deleting</code>, <code>Creating</code>, <code>Active</code></td>
    <td>Unknown</td>
    <td>No</td>
    </tr>
    <tr>
    <td>userMetadata</td>
    <td>userMetadata</td>
    <td>String</td>
    <td>Metadata associated with the queue</td>
    <td>-</td>
    <td>No</td>
    </tr>
    <tr>
    <td>enableBatchedOperations</td>
    <td>enableBatchedOperations</td>
    <td>Boolean</td>
    <td>Value that indicates whether server-side batched operations are enabled</td>
    <td>-</td>
    <td>No</td>
    </tr>
    <tr>
    <td>deadLetteringOnMessageExpiration</td>
    <td>deadLetteringOnMessageExpiration</td>
    <td>Boolean</td>
    <td>Value that indicates whether this queue has dead letter support when a message expires</td>
    <td>-</td>
    <td>No</td>
    </tr>
    <tr>
    <td>requiresDuplicateDetection</td>
    <td>requiresDuplicateDetection</td>
    <td>Boolean</td>
    <td>Value indicating if this queue requires duplicate detection</td>
    <td>-</td>
    <td>No</td>
    </tr>
    <tr>
    <td>enablePartitioning</td>
    <td>enablePartitioning</td>
    <td>Boolean</td>
    <td>Value that indicates whether the queue is to be partitioned across multiple message brokers</td>
    <td>-</td>
    <td>No</td>
    </tr>
    <tr>
    <td>requiresSession</td>
    <td>requiresSession</td>
    <td>Boolean</td>
    <td>Value that indicates whether the queue supports the concept of sessions</td>
    <td>-</td>
    <td>No</td>
    </tr>
    <tr>
    <td>supportOrdering</td>
    <td>supportOrdering</td>
    <td>Boolean</td>
    <td>Defines whether ordering needs to be maintained</td>
    <td>-</td>
    <td>No</td>
    </tr>
    <tr>
    <td>Output Variable Name</td>
    <td>responseVariable</td>
    <td>String</td>
    <td>The target variable in which the output of the operation will be stored</td>
    <td>-</td>
    <td>No</td>
    </tr>
    <tr>
    <td>Overwrite Message Body</td>
    <td>overwriteBody</td>
    <td>Boolean</td>
    <td>Replace the Message Body in Message Context with the output payload of the operation (This will remove the payload from the above variable. But other elements such as headers and attributes will remain).</td>
    <td>false</td>
    <td>No</td>
    </tr>
    </table>

    **Sample configuration**
    ```xml
    <asb.Administrator_createTopic configKey="CONNECTION_NAME">
        <topicName>{$ctx:topicName}</topicName>
        <status>{$ctx:status}</status>
        <responseVariable>asb_Administrator_createTopic_1</responseVariable>
        <overwriteBody>false</overwriteBody>
    </asb.Administrator_createTopic>
    ```

??? note "delete queue"
    Delete the queue with the given name.
    ```ballerina
    check admin->deleteQueue("queue-1");
    ```

    <table>
    <tr>
    <th>Parameter Name</th>
    <th>Element</th>
    <th>Type</th>
    <th>Description</th>
    <th>Default Value</th>
    <th>Required</th>
    </tr>
    <tr>
    <td>queueName</td>
    <td>queueName</td>
    <td>String</td>
    <td>Name of the queue</td>
    <td>-</td>
    <td>Yes</td>
    </tr>
    <tr>
    <td>Output Variable Name</td>
    <td>responseVariable</td>
    <td>String</td>
    <td>The target variable in which the output of the operation will be stored</td>
    <td>-</td>
    <td>No</td>
    </tr>
    <tr>
    <td>Overwrite Message Body</td>
    <td>overwriteBody</td>
    <td>Boolean</td>
    <td>Replace the Message Body in Message Context with the output payload of the operation (This will remove the payload from the above variable. But other elements such as headers and attributes will remain).</td>
    <td>false</td>
    <td>No</td>
    </tr>
    </table>

    **Sample configuration**
    ```xml
    <asb.Administrator_deleteQueue configKey="CONNECTION_NAME">
        <queueName>{$ctx:queueName}</queueName>
        <responseVariable>asb_Administrator_deleteQueue_1</responseVariable>
        <overwriteBody>false</overwriteBody>
    </asb.Administrator_deleteQueue>
    ```

??? note "delete rule"
    Delete the rule with the given name.
    ```ballerina
    check admin->deleteRule("topic-1", "sub-a", "rule-1");
    ```

    <table>
    <tr>
    <th>Parameter Name</th>
    <th>Element</th>
    <th>Type</th>
    <th>Description</th>
    <th>Default Value</th>
    <th>Required</th>
    </tr>
    <tr>
    <td>topicName</td>
    <td>topicName</td>
    <td>String</td>
    <td>Name of the topic associated with subscription</td>
    <td>-</td>
    <td>Yes</td>
    </tr>
    <tr>
    <td>subscriptionName</td>
    <td>subscriptionName</td>
    <td>String</td>
    <td>Name of the subscription associated with rule</td>
    <td>-</td>
    <td>Yes</td>
    </tr>
    <tr>
    <td>ruleName</td>
    <td>ruleName</td>
    <td>String</td>
    <td>Rule name</td>
    <td>-</td>
    <td>Yes</td>
    </tr>
    <tr>
    <td>Output Variable Name</td>
    <td>responseVariable</td>
    <td>String</td>
    <td>The target variable in which the output of the operation will be stored</td>
    <td>-</td>
    <td>No</td>
    </tr>
    <tr>
    <td>Overwrite Message Body</td>
    <td>overwriteBody</td>
    <td>Boolean</td>
    <td>Replace the Message Body in Message Context with the output payload of the operation (This will remove the payload from the above variable. But other elements such as headers and attributes will remain).</td>
    <td>false</td>
    <td>No</td>
    </tr>
    </table>

    **Sample configuration**
    ```xml
    <asb.Administrator_deleteRule configKey="CONNECTION_NAME">
        <topicName>{$ctx:topicName}</topicName>
        <subscriptionName>{$ctx:subscriptionName}</subscriptionName>
        <ruleName>{$ctx:ruleName}</ruleName>
        <responseVariable>asb_Administrator_deleteRule_1</responseVariable>
        <overwriteBody>false</overwriteBody>
    </asb.Administrator_deleteRule>
    ```

??? note "delete subscription"
    Delete the subscription with the given name.
    ```ballerina
    check admin->deleteSubscription("topic-1", "sub-a");
    ```

    <table>
    <tr>
    <th>Parameter Name</th>
    <th>Element</th>
    <th>Type</th>
    <th>Description</th>
    <th>Default Value</th>
    <th>Required</th>
    </tr>
    <tr>
    <td>topicName</td>
    <td>topicName</td>
    <td>String</td>
    <td>Topic name</td>
    <td>-</td>
    <td>Yes</td>
    </tr>
    <tr>
    <td>subscriptionName</td>
    <td>subscriptionName</td>
    <td>String</td>
    <td>Subscription name</td>
    <td>-</td>
    <td>Yes</td>
    </tr>
    <tr>
    <td>Output Variable Name</td>
    <td>responseVariable</td>
    <td>String</td>
    <td>The target variable in which the output of the operation will be stored</td>
    <td>-</td>
    <td>No</td>
    </tr>
    <tr>
    <td>Overwrite Message Body</td>
    <td>overwriteBody</td>
    <td>Boolean</td>
    <td>Replace the Message Body in Message Context with the output payload of the operation (This will remove the payload from the above variable. But other elements such as headers and attributes will remain).</td>
    <td>false</td>
    <td>No</td>
    </tr>
    </table>

    **Sample configuration**
    ```xml
    <asb.Administrator_deleteSubscription configKey="CONNECTION_NAME">
        <topicName>{$ctx:topicName}</topicName>
        <subscriptionName>{$ctx:subscriptionName}</subscriptionName>
        <responseVariable>asb_Administrator_deleteSubscription_1</responseVariable>
        <overwriteBody>false</overwriteBody>
    </asb.Administrator_deleteSubscription>
    ```

??? note "delete topic"
    Delete the topic with the given name.
    ```ballerina
    check admin->deleteTopic("topic-1");
    ```

    <table>
    <tr>
    <th>Parameter Name</th>
    <th>Element</th>
    <th>Type</th>
    <th>Description</th>
    <th>Default Value</th>
    <th>Required</th>
    </tr>
    <tr>
    <td>topicName</td>
    <td>topicName</td>
    <td>String</td>
    <td>Topic name</td>
    <td>-</td>
    <td>Yes</td>
    </tr>
    <tr>
    <td>Output Variable Name</td>
    <td>responseVariable</td>
    <td>String</td>
    <td>The target variable in which the output of the operation will be stored</td>
    <td>-</td>
    <td>No</td>
    </tr>
    <tr>
    <td>Overwrite Message Body</td>
    <td>overwriteBody</td>
    <td>Boolean</td>
    <td>Replace the Message Body in Message Context with the output payload of the operation (This will remove the payload from the above variable. But other elements such as headers and attributes will remain).</td>
    <td>false</td>
    <td>No</td>
    </tr>
    </table>

    **Sample configuration**
    ```xml
    <asb.Administrator_deleteTopic configKey="CONNECTION_NAME">
        <topicName>{$ctx:topicName}</topicName>
        <responseVariable>asb_Administrator_deleteTopic_1</responseVariable>
        <overwriteBody>false</overwriteBody>
    </asb.Administrator_deleteTopic>
    ```

??? note "get queue"
    Get the queue with the given name.
    ```ballerina
    asb:QueueProperties? queueProperties = check admin->getQueue("queue-1");
    ```

    <table>
    <tr>
    <th>Parameter Name</th>
    <th>Element</th>
    <th>Type</th>
    <th>Description</th>
    <th>Default Value</th>
    <th>Required</th>
    </tr>
    <tr>
    <td>queueName</td>
    <td>queueName</td>
    <td>String</td>
    <td>Name of the queue</td>
    <td>-</td>
    <td>Yes</td>
    </tr>
    <tr>
    <td>Output Variable Name</td>
    <td>responseVariable</td>
    <td>String</td>
    <td>The target variable in which the output of the operation will be stored</td>
    <td>-</td>
    <td>No</td>
    </tr>
    <tr>
    <td>Overwrite Message Body</td>
    <td>overwriteBody</td>
    <td>Boolean</td>
    <td>Replace the Message Body in Message Context with the output payload of the operation (This will remove the payload from the above variable. But other elements such as headers and attributes will remain).</td>
    <td>false</td>
    <td>No</td>
    </tr>
    </table>

    **Sample configuration**
    ```xml
    <asb.Administrator_getQueue configKey="CONNECTION_NAME">
        <queueName>{$ctx:queueName}</queueName>
        <responseVariable>asb_Administrator_getQueue_1</responseVariable>
        <overwriteBody>false</overwriteBody>
    </asb.Administrator_getQueue>
    ```

??? note "get rule"
    Get the rule with the given name.
    ```ballerina
    asb:RuleProperties? properties = check admin->getRule("topic-1", "sub-a", "rule-1");
    ```

    <table>
    <tr>
    <th>Parameter Name</th>
    <th>Element</th>
    <th>Type</th>
    <th>Description</th>
    <th>Default Value</th>
    <th>Required</th>
    </tr>
    <tr>
    <td>topicName</td>
    <td>topicName</td>
    <td>String</td>
    <td>Name of the topic associated with subscription</td>
    <td>-</td>
    <td>Yes</td>
    </tr>
    <tr>
    <td>subscriptionName</td>
    <td>subscriptionName</td>
    <td>String</td>
    <td>Name of the subscription associated with rule</td>
    <td>-</td>
    <td>Yes</td>
    </tr>
    <tr>
    <td>ruleName</td>
    <td>ruleName</td>
    <td>String</td>
    <td>Rule name</td>
    <td>-</td>
    <td>Yes</td>
    </tr>
    <tr>
    <td>Output Variable Name</td>
    <td>responseVariable</td>
    <td>String</td>
    <td>The target variable in which the output of the operation will be stored</td>
    <td>-</td>
    <td>No</td>
    </tr>
    <tr>
    <td>Overwrite Message Body</td>
    <td>overwriteBody</td>
    <td>Boolean</td>
    <td>Replace the Message Body in Message Context with the output payload of the operation (This will remove the payload from the above variable. But other elements such as headers and attributes will remain).</td>
    <td>false</td>
    <td>No</td>
    </tr>
    </table>

    **Sample configuration**
    ```xml
    <asb.Administrator_getRule configKey="CONNECTION_NAME">
        <topicName>{$ctx:topicName}</topicName>
        <subscriptionName>{$ctx:subscriptionName}</subscriptionName>
        <ruleName>{$ctx:ruleName}</ruleName>
        <responseVariable>asb_Administrator_getRule_1</responseVariable>
        <overwriteBody>false</overwriteBody>
    </asb.Administrator_getRule>
    ```

??? note "get subscription"
    Get the subscription with the given name.
    ```ballerina
    asb:SubscriptionProperties? subscriptionProperties = check admin->getSubscription("topic-1", "sub-a");
    ```

    <table>
    <tr>
    <th>Parameter Name</th>
    <th>Element</th>
    <th>Type</th>
    <th>Description</th>
    <th>Default Value</th>
    <th>Required</th>
    </tr>
    <tr>
    <td>topicName</td>
    <td>topicName</td>
    <td>String</td>
    <td>Name of the topic associated with subscription</td>
    <td>-</td>
    <td>Yes</td>
    </tr>
    <tr>
    <td>subscriptionName</td>
    <td>subscriptionName</td>
    <td>String</td>
    <td>Name of the subscription</td>
    <td>-</td>
    <td>Yes</td>
    </tr>
    <tr>
    <td>Output Variable Name</td>
    <td>responseVariable</td>
    <td>String</td>
    <td>The target variable in which the output of the operation will be stored</td>
    <td>-</td>
    <td>No</td>
    </tr>
    <tr>
    <td>Overwrite Message Body</td>
    <td>overwriteBody</td>
    <td>Boolean</td>
    <td>Replace the Message Body in Message Context with the output payload of the operation (This will remove the payload from the above variable. But other elements such as headers and attributes will remain).</td>
    <td>false</td>
    <td>No</td>
    </tr>
    </table>

    **Sample configuration**
    ```xml
    <asb.Administrator_getSubscription configKey="CONNECTION_NAME">
        <topicName>{$ctx:topicName}</topicName>
        <subscriptionName>{$ctx:subscriptionName}</subscriptionName>
        <responseVariable>asb_Administrator_getSubscription_1</responseVariable>
        <overwriteBody>false</overwriteBody>
    </asb.Administrator_getSubscription>
    ```

??? note "get topic"
    Get the topic with the given name.
    ```ballerina
    asb:TopicProperties? topicProperties = check admin->getTopic("topic-1");
    ```

    <table>
    <tr>
    <th>Parameter Name</th>
    <th>Element</th>
    <th>Type</th>
    <th>Description</th>
    <th>Default Value</th>
    <th>Required</th>
    </tr>
    <tr>
    <td>topicName</td>
    <td>topicName</td>
    <td>String</td>
    <td>Topic name</td>
    <td>-</td>
    <td>Yes</td>
    </tr>
    <tr>
    <td>Output Variable Name</td>
    <td>responseVariable</td>
    <td>String</td>
    <td>The target variable in which the output of the operation will be stored</td>
    <td>-</td>
    <td>No</td>
    </tr>
    <tr>
    <td>Overwrite Message Body</td>
    <td>overwriteBody</td>
    <td>Boolean</td>
    <td>Replace the Message Body in Message Context with the output payload of the operation (This will remove the payload from the above variable. But other elements such as headers and attributes will remain).</td>
    <td>false</td>
    <td>No</td>
    </tr>
    </table>

    **Sample configuration**
    ```xml
    <asb.Administrator_getTopic configKey="CONNECTION_NAME">
        <topicName>{$ctx:topicName}</topicName>
        <responseVariable>asb_Administrator_getTopic_1</responseVariable>
        <overwriteBody>false</overwriteBody>
    </asb.Administrator_getTopic>
    ```

??? note "list queues"
    List the queues.
    ```ballerina
    asb:QueueList? queues = check admin->listQueues();
    ```

    <table>
    <tr>
    <th>Parameter Name</th>
    <th>Element</th>
    <th>Type</th>
    <th>Description</th>
    <th>Default Value</th>
    <th>Required</th>
    </tr>
    <tr>
    <td>Output Variable Name</td>
    <td>responseVariable</td>
    <td>String</td>
    <td>The target variable in which the output of the operation will be stored</td>
    <td>-</td>
    <td>No</td>
    </tr>
    <tr>
    <td>Overwrite Message Body</td>
    <td>overwriteBody</td>
    <td>Boolean</td>
    <td>Replace the Message Body in Message Context with the output payload of the operation (This will remove the payload from the above variable. But other elements such as headers and attributes will remain).</td>
    <td>false</td>
    <td>No</td>
    </tr>
    </table>

    **Sample configuration**
    ```xml
    <asb.Administrator_listQueues configKey="CONNECTION_NAME">
        <responseVariable>asb_Administrator_listQueues_1</responseVariable>
        <overwriteBody>false</overwriteBody>
    </asb.Administrator_listQueues>
    ```

??? note "list rules"
    List the rules.
    ```ballerina
    asb:RuleList? rules = check admin->listRules("topic-1", "sub-a");
    ```

    <table>
    <tr>
    <th>Parameter Name</th>
    <th>Element</th>
    <th>Type</th>
    <th>Description</th>
    <th>Default Value</th>
    <th>Required</th>
    </tr>
    <tr>
    <td>topicName</td>
    <td>topicName</td>
    <td>String</td>
    <td>Name of the topic associated with subscription</td>
    <td>-</td>
    <td>Yes</td>
    </tr>
    <tr>
    <td>subscriptionName</td>
    <td>subscriptionName</td>
    <td>String</td>
    <td>Name of the subscription</td>
    <td>-</td>
    <td>Yes</td>
    </tr>
    <tr>
    <td>Output Variable Name</td>
    <td>responseVariable</td>
    <td>String</td>
    <td>The target variable in which the output of the operation will be stored</td>
    <td>-</td>
    <td>No</td>
    </tr>
    <tr>
    <td>Overwrite Message Body</td>
    <td>overwriteBody</td>
    <td>Boolean</td>
    <td>Replace the Message Body in Message Context with the output payload of the operation (This will remove the payload from the above variable. But other elements such as headers and attributes will remain).</td>
    <td>false</td>
    <td>No</td>
    </tr>
    </table>

    **Sample configuration**
    ```xml
    <asb.Administrator_listRules configKey="CONNECTION_NAME">
        <topicName>{$ctx:topicName}</topicName>
        <subscriptionName>{$ctx:subscriptionName}</subscriptionName>
        <responseVariable>asb_Administrator_listRules_1</responseVariable>
        <overwriteBody>false</overwriteBody>
    </asb.Administrator_listRules>
    ```

??? note "list subscriptions"
    List the subscriptions.
    ```ballerina
    asb:SubscriptionList? subscriptions = check admin->listSubscriptions("topic-1");
    ```

    <table>
    <tr>
    <th>Parameter Name</th>
    <th>Element</th>
    <th>Type</th>
    <th>Description</th>
    <th>Default Value</th>
    <th>Required</th>
    </tr>
    <tr>
    <td>topicName</td>
    <td>topicName</td>
    <td>String</td>
    <td>Name of the topic associated with subscription</td>
    <td>-</td>
    <td>Yes</td>
    </tr>
    <tr>
    <td>Output Variable Name</td>
    <td>responseVariable</td>
    <td>String</td>
    <td>The target variable in which the output of the operation will be stored</td>
    <td>-</td>
    <td>No</td>
    </tr>
    <tr>
    <td>Overwrite Message Body</td>
    <td>overwriteBody</td>
    <td>Boolean</td>
    <td>Replace the Message Body in Message Context with the output payload of the operation (This will remove the payload from the above variable. But other elements such as headers and attributes will remain).</td>
    <td>false</td>
    <td>No</td>
    </tr>
    </table>

    **Sample configuration**
    ```xml
    <asb.Administrator_listSubscriptions configKey="CONNECTION_NAME">
        <topicName>{$ctx:topicName}</topicName>
        <responseVariable>asb_Administrator_listSubscriptions_1</responseVariable>
        <overwriteBody>false</overwriteBody>
    </asb.Administrator_listSubscriptions>
    ```

??? note "list topics"
    List the topics.
    ```ballerina
    asb:TopicList? topics = check admin->listTopics();
    ```

    <table>
    <tr>
    <th>Parameter Name</th>
    <th>Element</th>
    <th>Type</th>
    <th>Description</th>
    <th>Default Value</th>
    <th>Required</th>
    </tr>
    <tr>
    <td>Output Variable Name</td>
    <td>responseVariable</td>
    <td>String</td>
    <td>The target variable in which the output of the operation will be stored</td>
    <td>-</td>
    <td>No</td>
    </tr>
    <tr>
    <td>Overwrite Message Body</td>
    <td>overwriteBody</td>
    <td>Boolean</td>
    <td>Replace the Message Body in Message Context with the output payload of the operation (This will remove the payload from the above variable. But other elements such as headers and attributes will remain).</td>
    <td>false</td>
    <td>No</td>
    </tr>
    </table>

    **Sample configuration**
    ```xml
    <asb.Administrator_listTopics configKey="CONNECTION_NAME">
        <responseVariable>asb_Administrator_listTopics_1</responseVariable>
        <overwriteBody>false</overwriteBody>
    </asb.Administrator_listTopics>
    ```

??? note "queue exists"
    Check whether the queue exists.
    ```ballerina
    boolean exists = check admin->queueExists("queue-1");
    ```

    <table>
    <tr>
    <th>Parameter Name</th>
    <th>Element</th>
    <th>Type</th>
    <th>Description</th>
    <th>Default Value</th>
    <th>Required</th>
    </tr>
    <tr>
    <td>queueName</td>
    <td>queueName</td>
    <td>String</td>
    <td>Name of the queue</td>
    <td>-</td>
    <td>Yes</td>
    </tr>
    <tr>
    <td>Output Variable Name</td>
    <td>responseVariable</td>
    <td>String</td>
    <td>The target variable in which the output of the operation will be stored</td>
    <td>-</td>
    <td>No</td>
    </tr>
    <tr>
    <td>Overwrite Message Body</td>
    <td>overwriteBody</td>
    <td>Boolean</td>
    <td>Replace the Message Body in Message Context with the output payload of the operation (This will remove the payload from the above variable. But other elements such as headers and attributes will remain).</td>
    <td>false</td>
    <td>No</td>
    </tr>
    </table>

    **Sample configuration**
    ```xml
    <asb.Administrator_queueExists configKey="CONNECTION_NAME">
        <queueName>{$ctx:queueName}</queueName>
        <responseVariable>asb_Administrator_queueExists_1</responseVariable>
        <overwriteBody>false</overwriteBody>
    </asb.Administrator_queueExists>
    ```

??? note "subscription exists"
    Get the status of existance of a subscription with the given name.
    ```ballerina
    boolean exists = check admin->subscriptionExists("topic-1", "sub-a");
    ```

    <table>
    <tr>
    <th>Parameter Name</th>
    <th>Element</th>
    <th>Type</th>
    <th>Description</th>
    <th>Default Value</th>
    <th>Required</th>
    </tr>
    <tr>
    <td>topicName</td>
    <td>topicName</td>
    <td>String</td>
    <td>Topic name</td>
    <td>-</td>
    <td>Yes</td>
    </tr>
    <tr>
    <td>subscriptionName</td>
    <td>subscriptionName</td>
    <td>String</td>
    <td>Subscription name</td>
    <td>-</td>
    <td>Yes</td>
    </tr>
    <tr>
    <td>Output Variable Name</td>
    <td>responseVariable</td>
    <td>String</td>
    <td>The target variable in which the output of the operation will be stored</td>
    <td>-</td>
    <td>No</td>
    </tr>
    <tr>
    <td>Overwrite Message Body</td>
    <td>overwriteBody</td>
    <td>Boolean</td>
    <td>Replace the Message Body in Message Context with the output payload of the operation (This will remove the payload from the above variable. But other elements such as headers and attributes will remain).</td>
    <td>false</td>
    <td>No</td>
    </tr>
    </table>

    **Sample configuration**
    ```xml
    <asb.Administrator_subscriptionExists configKey="CONNECTION_NAME">
        <topicName>{$ctx:topicName}</topicName>
        <subscriptionName>{$ctx:subscriptionName}</subscriptionName>
        <responseVariable>asb_Administrator_subscriptionExists_1</responseVariable>
        <overwriteBody>false</overwriteBody>
    </asb.Administrator_subscriptionExists>
    ```

??? note "topic exists"
    Get the status of existance of a topic with the given name.
    ```ballerina
    boolean exists = check admin->topicExists("topic-1");
    ```

    <table>
    <tr>
    <th>Parameter Name</th>
    <th>Element</th>
    <th>Type</th>
    <th>Description</th>
    <th>Default Value</th>
    <th>Required</th>
    </tr>
    <tr>
    <td>topicName</td>
    <td>topicName</td>
    <td>String</td>
    <td>Topic name</td>
    <td>-</td>
    <td>Yes</td>
    </tr>
    <tr>
    <td>Output Variable Name</td>
    <td>responseVariable</td>
    <td>String</td>
    <td>The target variable in which the output of the operation will be stored</td>
    <td>-</td>
    <td>No</td>
    </tr>
    <tr>
    <td>Overwrite Message Body</td>
    <td>overwriteBody</td>
    <td>Boolean</td>
    <td>Replace the Message Body in Message Context with the output payload of the operation (This will remove the payload from the above variable. But other elements such as headers and attributes will remain).</td>
    <td>false</td>
    <td>No</td>
    </tr>
    </table>

    **Sample configuration**
    ```xml
    <asb.Administrator_topicExists configKey="CONNECTION_NAME">
        <topicName>{$ctx:topicName}</topicName>
        <responseVariable>asb_Administrator_topicExists_1</responseVariable>
        <overwriteBody>false</overwriteBody>
    </asb.Administrator_topicExists>
    ```

??? note "update queue"
    Update the queue with the options.
    ```ballerina
    asb:QueueProperties? queueProperties = check admin->updateQueue("queue-1", maxDeliveryCount = 10);
    ```

    <table>
    <tr>
    <th>Parameter Name</th>
    <th>Element</th>
    <th>Type</th>
    <th>Description</th>
    <th>Default Value</th>
    <th>Required</th>
    </tr>
    <tr>
    <td>queueName</td>
    <td>queueName</td>
    <td>String</td>
    <td>Name of the queue</td>
    <td>-</td>
    <td>Yes</td>
    </tr>
    <tr>
    <td>seconds<br/><small>(Auto Delete On Idle)</small></td>
    <td>autoDeleteOnIdle.seconds</td>
    <td>String</td>
    <td>Seconds</td>
    <td>-</td>
    <td>No</td>
    </tr>
    <tr>
    <td>nanoseconds<br/><small>(Auto Delete On Idle)</small></td>
    <td>autoDeleteOnIdle.nanoseconds</td>
    <td>String</td>
    <td>Nanoseconds</td>
    <td>-</td>
    <td>No</td>
    </tr>
    <tr>
    <td>seconds<br/><small>(Default Message Time To Live)</small></td>
    <td>defaultMessageTimeToLive.seconds</td>
    <td>String</td>
    <td>Seconds</td>
    <td>-</td>
    <td>No</td>
    </tr>
    <tr>
    <td>nanoseconds<br/><small>(Default Message Time To Live)</small></td>
    <td>defaultMessageTimeToLive.nanoseconds</td>
    <td>String</td>
    <td>Nanoseconds</td>
    <td>-</td>
    <td>No</td>
    </tr>
    <tr>
    <td>seconds<br/><small>(Duplicate Detection History Time Window)</small></td>
    <td>duplicateDetectionHistoryTimeWindow.seconds</td>
    <td>String</td>
    <td>Seconds</td>
    <td>-</td>
    <td>No</td>
    </tr>
    <tr>
    <td>nanoseconds<br/><small>(Duplicate Detection History Time Window)</small></td>
    <td>duplicateDetectionHistoryTimeWindow.nanoseconds</td>
    <td>String</td>
    <td>Nanoseconds</td>
    <td>-</td>
    <td>No</td>
    </tr>
    <tr>
    <td>forwardDeadLetteredMessagesTo</td>
    <td>forwardDeadLetteredMessagesTo</td>
    <td>String</td>
    <td>The name of the recipient entity to which all the dead-lettered messages of this subscription are forwarded to.</td>
    <td>-</td>
    <td>No</td>
    </tr>
    <tr>
    <td>forwardTo</td>
    <td>forwardTo</td>
    <td>String</td>
    <td>The name of the recipient entity to which all the messages sent to the queue are forwarded to</td>
    <td>-</td>
    <td>No</td>
    </tr>
    <tr>
    <td>seconds<br/><small>(Lock Duration)</small></td>
    <td>lockDuration.seconds</td>
    <td>String</td>
    <td>Seconds</td>
    <td>-</td>
    <td>No</td>
    </tr>
    <tr>
    <td>nanoseconds<br/><small>(Lock Duration)</small></td>
    <td>lockDuration.nanoseconds</td>
    <td>String</td>
    <td>Nanoseconds</td>
    <td>-</td>
    <td>No</td>
    </tr>
    <tr>
    <td>maxDeliveryCount</td>
    <td>maxDeliveryCount</td>
    <td>String</td>
    <td>The maximum delivery count. A message is automatically deadlettered after this number of deliveries. Default value is 10.</td>
    <td>-</td>
    <td>No</td>
    </tr>
    <tr>
    <td>maxMessageSizeInKilobytes</td>
    <td>maxMessageSizeInKilobytes</td>
    <td>String</td>
    <td>The maximum size of the queue in megabytes, which is the size of memory allocated for the queue</td>
    <td>-</td>
    <td>No</td>
    </tr>
    <tr>
    <td>maxSizeInMegabytes</td>
    <td>maxSizeInMegabytes</td>
    <td>String</td>
    <td>The maximum size of the queue in megabytes, which is the size of memory allocated for the queue</td>
    <td>-</td>
    <td>No</td>
    </tr>
    <tr>
    <td>status</td>
    <td>status</td>
    <td>Enum</td>
    <td>Enumerates the possible values for the status of a messaging entity<br/><b>Possible values</b>: <code>Unknown</code>, <code>SendDisabled</code>, <code>Restoring</code>, <code>Renaming</code>, <code>ReceiveDisabled</code>, <code>Disabled</code>, <code>Deleting</code>, <code>Creating</code>, <code>Active</code></td>
    <td>Unknown</td>
    <td>No</td>
    </tr>
    <tr>
    <td>userMetadata</td>
    <td>userMetadata</td>
    <td>String</td>
    <td>Metadata associated with the queue</td>
    <td>-</td>
    <td>No</td>
    </tr>
    <tr>
    <td>enableBatchedOperations</td>
    <td>enableBatchedOperations</td>
    <td>Boolean</td>
    <td>Value that indicates whether server-side batched operations are enabled</td>
    <td>-</td>
    <td>No</td>
    </tr>
    <tr>
    <td>deadLetteringOnMessageExpiration</td>
    <td>deadLetteringOnMessageExpiration</td>
    <td>Boolean</td>
    <td>Value that indicates whether this queue has dead letter support when a message expires</td>
    <td>-</td>
    <td>No</td>
    </tr>
    <tr>
    <td>requiresDuplicateDetection</td>
    <td>requiresDuplicateDetection</td>
    <td>Boolean</td>
    <td>Value indicating if this queue requires duplicate detection</td>
    <td>-</td>
    <td>No</td>
    </tr>
    <tr>
    <td>enablePartitioning</td>
    <td>enablePartitioning</td>
    <td>Boolean</td>
    <td>Value that indicates whether the queue is to be partitioned across multiple message brokers</td>
    <td>-</td>
    <td>No</td>
    </tr>
    <tr>
    <td>requiresSession</td>
    <td>requiresSession</td>
    <td>Boolean</td>
    <td>Value that indicates whether the queue supports the concept of sessions</td>
    <td>-</td>
    <td>No</td>
    </tr>
    <tr>
    <td>Output Variable Name</td>
    <td>responseVariable</td>
    <td>String</td>
    <td>The target variable in which the output of the operation will be stored</td>
    <td>-</td>
    <td>No</td>
    </tr>
    <tr>
    <td>Overwrite Message Body</td>
    <td>overwriteBody</td>
    <td>Boolean</td>
    <td>Replace the Message Body in Message Context with the output payload of the operation (This will remove the payload from the above variable. But other elements such as headers and attributes will remain).</td>
    <td>false</td>
    <td>No</td>
    </tr>
    </table>

    **Sample configuration**
    ```xml
    <asb.Administrator_updateQueue configKey="CONNECTION_NAME">
        <queueName>{$ctx:queueName}</queueName>
        <status>{$ctx:status}</status>
        <responseVariable>asb_Administrator_updateQueue_1</responseVariable>
        <overwriteBody>false</overwriteBody>
    </asb.Administrator_updateQueue>
    ```

??? note "update rule"
    Update the rule with the options.
    ```ballerina
    asb:SqlRule rule = ...;
    asb:RuleProperties? ruleProperties = check admin->updateRule("topic-1", "sub-a", "rule-1", rule = rule);
    ```

    <table>
    <tr>
    <th>Parameter Name</th>
    <th>Element</th>
    <th>Type</th>
    <th>Description</th>
    <th>Default Value</th>
    <th>Required</th>
    </tr>
    <tr>
    <td>topicName</td>
    <td>topicName</td>
    <td>String</td>
    <td>Name of the topic associated with subscription</td>
    <td>-</td>
    <td>Yes</td>
    </tr>
    <tr>
    <td>subscriptionName</td>
    <td>subscriptionName</td>
    <td>String</td>
    <td>Name of the subscription associated with rule</td>
    <td>-</td>
    <td>Yes</td>
    </tr>
    <tr>
    <td>ruleName</td>
    <td>ruleName</td>
    <td>String</td>
    <td>Rule name</td>
    <td>-</td>
    <td>Yes</td>
    </tr>
    <tr>
    <td>filter<br/><small>(Rule)</small></td>
    <td>rule_filter</td>
    <td>String</td>
    <td>-</td>
    <td>-</td>
    <td>No</td>
    </tr>
    <tr>
    <td>action<br/><small>(Rule)</small></td>
    <td>rule_action</td>
    <td>String</td>
    <td>-</td>
    <td>-</td>
    <td>No</td>
    </tr>
    <tr>
    <td>Output Variable Name</td>
    <td>responseVariable</td>
    <td>String</td>
    <td>The target variable in which the output of the operation will be stored</td>
    <td>-</td>
    <td>No</td>
    </tr>
    <tr>
    <td>Overwrite Message Body</td>
    <td>overwriteBody</td>
    <td>Boolean</td>
    <td>Replace the Message Body in Message Context with the output payload of the operation (This will remove the payload from the above variable. But other elements such as headers and attributes will remain).</td>
    <td>false</td>
    <td>No</td>
    </tr>
    </table>

    **Sample configuration**
    ```xml
    <asb.Administrator_updateRule configKey="CONNECTION_NAME">
        <topicName>{$ctx:topicName}</topicName>
        <subscriptionName>{$ctx:subscriptionName}</subscriptionName>
        <ruleName>{$ctx:ruleName}</ruleName>
        <responseVariable>asb_Administrator_updateRule_1</responseVariable>
        <overwriteBody>false</overwriteBody>
    </asb.Administrator_updateRule>
    ```

??? note "update subscription"
    Update the subscription with the given options.
    ```ballerina
    asb:SubscriptionProperties? subProp = check admin->updateSubscription("topic-1", "sub-a", maxDeliveryCount = 10);
    ```

    <table>
    <tr>
    <th>Parameter Name</th>
    <th>Element</th>
    <th>Type</th>
    <th>Description</th>
    <th>Default Value</th>
    <th>Required</th>
    </tr>
    <tr>
    <td>topicName</td>
    <td>topicName</td>
    <td>String</td>
    <td>Name of the topic associated with subscription</td>
    <td>-</td>
    <td>Yes</td>
    </tr>
    <tr>
    <td>subscriptionName</td>
    <td>subscriptionName</td>
    <td>String</td>
    <td>Name of the subscription</td>
    <td>-</td>
    <td>Yes</td>
    </tr>
    <tr>
    <td>seconds<br/><small>(Auto Delete On Idle)</small></td>
    <td>autoDeleteOnIdle.seconds</td>
    <td>String</td>
    <td>Seconds</td>
    <td>-</td>
    <td>No</td>
    </tr>
    <tr>
    <td>nanoseconds<br/><small>(Auto Delete On Idle)</small></td>
    <td>autoDeleteOnIdle.nanoseconds</td>
    <td>String</td>
    <td>Nanoseconds</td>
    <td>-</td>
    <td>No</td>
    </tr>
    <tr>
    <td>seconds<br/><small>(Default Message Time To Live)</small></td>
    <td>defaultMessageTimeToLive.seconds</td>
    <td>String</td>
    <td>Seconds</td>
    <td>-</td>
    <td>No</td>
    </tr>
    <tr>
    <td>nanoseconds<br/><small>(Default Message Time To Live)</small></td>
    <td>defaultMessageTimeToLive.nanoseconds</td>
    <td>String</td>
    <td>Nanoseconds</td>
    <td>-</td>
    <td>No</td>
    </tr>
    <tr>
    <td>deadLetteringOnMessageExpiration</td>
    <td>deadLetteringOnMessageExpiration</td>
    <td>Boolean</td>
    <td>Value that indicates whether this queue has dead letter support when a message expires</td>
    <td>-</td>
    <td>No</td>
    </tr>
    <tr>
    <td>deadLetteringOnFilterEvaluationExceptions</td>
    <td>deadLetteringOnFilterEvaluationExceptions</td>
    <td>Boolean</td>
    <td>Value that indicates whether this subscription has dead letter support when a message expires</td>
    <td>-</td>
    <td>No</td>
    </tr>
    <tr>
    <td>enableBatchedOperations</td>
    <td>enableBatchedOperations</td>
    <td>Boolean</td>
    <td>Value that indicates whether server-side batched operations are enabled</td>
    <td>-</td>
    <td>No</td>
    </tr>
    <tr>
    <td>forwardDeadLetteredMessagesTo</td>
    <td>forwardDeadLetteredMessagesTo</td>
    <td>String</td>
    <td>The name of the recipient entity to which all the dead-lettered messages of this subscription are forwarded to.</td>
    <td>-</td>
    <td>No</td>
    </tr>
    <tr>
    <td>forwardTo</td>
    <td>forwardTo</td>
    <td>String</td>
    <td>The name of the recipient entity to which all the messages sent to the queue are forwarded to</td>
    <td>-</td>
    <td>No</td>
    </tr>
    <tr>
    <td>seconds<br/><small>(Lock Duration)</small></td>
    <td>lockDuration.seconds</td>
    <td>String</td>
    <td>Seconds</td>
    <td>-</td>
    <td>No</td>
    </tr>
    <tr>
    <td>nanoseconds<br/><small>(Lock Duration)</small></td>
    <td>lockDuration.nanoseconds</td>
    <td>String</td>
    <td>Nanoseconds</td>
    <td>-</td>
    <td>No</td>
    </tr>
    <tr>
    <td>maxDeliveryCount</td>
    <td>maxDeliveryCount</td>
    <td>String</td>
    <td>The maximum delivery count. A message is automatically deadlettered after this number of deliveries. Default value is 10.</td>
    <td>-</td>
    <td>No</td>
    </tr>
    <tr>
    <td>status</td>
    <td>status</td>
    <td>Enum</td>
    <td>Enumerates the possible values for the status of a messaging entity<br/><b>Possible values</b>: <code>Unknown</code>, <code>SendDisabled</code>, <code>Restoring</code>, <code>Renaming</code>, <code>ReceiveDisabled</code>, <code>Disabled</code>, <code>Deleting</code>, <code>Creating</code>, <code>Active</code></td>
    <td>Unknown</td>
    <td>No</td>
    </tr>
    <tr>
    <td>userMetadata</td>
    <td>userMetadata</td>
    <td>String</td>
    <td>Metadata associated with the queue</td>
    <td>-</td>
    <td>No</td>
    </tr>
    <tr>
    <td>Output Variable Name</td>
    <td>responseVariable</td>
    <td>String</td>
    <td>The target variable in which the output of the operation will be stored</td>
    <td>-</td>
    <td>No</td>
    </tr>
    <tr>
    <td>Overwrite Message Body</td>
    <td>overwriteBody</td>
    <td>Boolean</td>
    <td>Replace the Message Body in Message Context with the output payload of the operation (This will remove the payload from the above variable. But other elements such as headers and attributes will remain).</td>
    <td>false</td>
    <td>No</td>
    </tr>
    </table>

    **Sample configuration**
    ```xml
    <asb.Administrator_updateSubscription configKey="CONNECTION_NAME">
        <topicName>{$ctx:topicName}</topicName>
        <subscriptionName>{$ctx:subscriptionName}</subscriptionName>
        <status>{$ctx:status}</status>
        <responseVariable>asb_Administrator_updateSubscription_1</responseVariable>
        <overwriteBody>false</overwriteBody>
    </asb.Administrator_updateSubscription>
    ```

??? note "update topic"
    Update the topic with the given options.
    ```ballerina
    asb:TopicProperties? topicProp = check admin->updateTopic("topic-1", supportOrdering = true);
    ```

    <table>
    <tr>
    <th>Parameter Name</th>
    <th>Element</th>
    <th>Type</th>
    <th>Description</th>
    <th>Default Value</th>
    <th>Required</th>
    </tr>
    <tr>
    <td>topicName</td>
    <td>topicName</td>
    <td>String</td>
    <td>Topic name</td>
    <td>-</td>
    <td>Yes</td>
    </tr>
    <tr>
    <td>seconds<br/><small>(Auto Delete On Idle)</small></td>
    <td>autoDeleteOnIdle.seconds</td>
    <td>String</td>
    <td>Seconds</td>
    <td>-</td>
    <td>No</td>
    </tr>
    <tr>
    <td>nanoseconds<br/><small>(Auto Delete On Idle)</small></td>
    <td>autoDeleteOnIdle.nanoseconds</td>
    <td>String</td>
    <td>Nanoseconds</td>
    <td>-</td>
    <td>No</td>
    </tr>
    <tr>
    <td>seconds<br/><small>(Default Message Time To Live)</small></td>
    <td>defaultMessageTimeToLive.seconds</td>
    <td>String</td>
    <td>Seconds</td>
    <td>-</td>
    <td>No</td>
    </tr>
    <tr>
    <td>nanoseconds<br/><small>(Default Message Time To Live)</small></td>
    <td>defaultMessageTimeToLive.nanoseconds</td>
    <td>String</td>
    <td>Nanoseconds</td>
    <td>-</td>
    <td>No</td>
    </tr>
    <tr>
    <td>seconds<br/><small>(Duplicate Detection History Time Window)</small></td>
    <td>duplicateDetectionHistoryTimeWindow.seconds</td>
    <td>String</td>
    <td>Seconds</td>
    <td>-</td>
    <td>No</td>
    </tr>
    <tr>
    <td>nanoseconds<br/><small>(Duplicate Detection History Time Window)</small></td>
    <td>duplicateDetectionHistoryTimeWindow.nanoseconds</td>
    <td>String</td>
    <td>Nanoseconds</td>
    <td>-</td>
    <td>No</td>
    </tr>
    <tr>
    <td>maxDeliveryCount</td>
    <td>maxDeliveryCount</td>
    <td>String</td>
    <td>The maximum delivery count. A message is automatically deadlettered after this number of deliveries. Default value is 10.</td>
    <td>-</td>
    <td>No</td>
    </tr>
    <tr>
    <td>maxMessageSizeInKilobytes</td>
    <td>maxMessageSizeInKilobytes</td>
    <td>String</td>
    <td>The maximum size of the queue in megabytes, which is the size of memory allocated for the queue</td>
    <td>-</td>
    <td>No</td>
    </tr>
    <tr>
    <td>maxSizeInMegabytes</td>
    <td>maxSizeInMegabytes</td>
    <td>String</td>
    <td>The maximum size of the queue in megabytes, which is the size of memory allocated for the queue</td>
    <td>-</td>
    <td>No</td>
    </tr>
    <tr>
    <td>status</td>
    <td>status</td>
    <td>Enum</td>
    <td>Enumerates the possible values for the status of a messaging entity<br/><b>Possible values</b>: <code>Unknown</code>, <code>SendDisabled</code>, <code>Restoring</code>, <code>Renaming</code>, <code>ReceiveDisabled</code>, <code>Disabled</code>, <code>Deleting</code>, <code>Creating</code>, <code>Active</code></td>
    <td>Unknown</td>
    <td>No</td>
    </tr>
    <tr>
    <td>userMetadata</td>
    <td>userMetadata</td>
    <td>String</td>
    <td>Metadata associated with the queue</td>
    <td>-</td>
    <td>No</td>
    </tr>
    <tr>
    <td>enableBatchedOperations</td>
    <td>enableBatchedOperations</td>
    <td>Boolean</td>
    <td>Value that indicates whether server-side batched operations are enabled</td>
    <td>-</td>
    <td>No</td>
    </tr>
    <tr>
    <td>deadLetteringOnMessageExpiration</td>
    <td>deadLetteringOnMessageExpiration</td>
    <td>Boolean</td>
    <td>Value that indicates whether this queue has dead letter support when a message expires</td>
    <td>-</td>
    <td>No</td>
    </tr>
    <tr>
    <td>requiresDuplicateDetection</td>
    <td>requiresDuplicateDetection</td>
    <td>Boolean</td>
    <td>Value indicating if this queue requires duplicate detection</td>
    <td>-</td>
    <td>No</td>
    </tr>
    <tr>
    <td>enablePartitioning</td>
    <td>enablePartitioning</td>
    <td>Boolean</td>
    <td>Value that indicates whether the queue is to be partitioned across multiple message brokers</td>
    <td>-</td>
    <td>No</td>
    </tr>
    <tr>
    <td>requiresSession</td>
    <td>requiresSession</td>
    <td>Boolean</td>
    <td>Value that indicates whether the queue supports the concept of sessions</td>
    <td>-</td>
    <td>No</td>
    </tr>
    <tr>
    <td>supportOrdering</td>
    <td>supportOrdering</td>
    <td>Boolean</td>
    <td>Defines whether ordering needs to be maintained</td>
    <td>-</td>
    <td>No</td>
    </tr>
    <tr>
    <td>Output Variable Name</td>
    <td>responseVariable</td>
    <td>String</td>
    <td>The target variable in which the output of the operation will be stored</td>
    <td>-</td>
    <td>No</td>
    </tr>
    <tr>
    <td>Overwrite Message Body</td>
    <td>overwriteBody</td>
    <td>Boolean</td>
    <td>Replace the Message Body in Message Context with the output payload of the operation (This will remove the payload from the above variable. But other elements such as headers and attributes will remain).</td>
    <td>false</td>
    <td>No</td>
    </tr>
    </table>

    **Sample configuration**
    ```xml
    <asb.Administrator_updateTopic configKey="CONNECTION_NAME">
        <topicName>{$ctx:topicName}</topicName>
        <status>{$ctx:status}</status>
        <responseVariable>asb_Administrator_updateTopic_1</responseVariable>
        <overwriteBody>false</overwriteBody>
    </asb.Administrator_updateTopic>
    ```

### MessageReceiver

??? note "abandon"
    Abandon message from queue or subscription based on messageLockToken. Abandon processing of the message for 
    the time being, returning the message immediately back to the queue to be picked up by another (or the same) 
    receiver.
    ```ballerina
    asb:Message message = ...;
    check receiver->abandon(message);
    ```

    <table>
    <tr>
    <th>Parameter Name</th>
    <th>Element</th>
    <th>Type</th>
    <th>Description</th>
    <th>Default Value</th>
    <th>Required</th>
    </tr>
    <tr>
    <td>body</td>
    <td>body</td>
    <td>String</td>
    <td>Expecting JSON object</td>
    <td>-</td>
    <td>Yes</td>
    </tr>
    <tr>
    <td>contentType</td>
    <td>contentType</td>
    <td>String</td>
    <td>Message content type, with a descriptor following the format of `RFC2045`, (e.g. `application/json`) (optional)</td>
    <td>-</td>
    <td>No</td>
    </tr>
    <tr>
    <td>messageId</td>
    <td>messageId</td>
    <td>String</td>
    <td>Message Id (optional)</td>
    <td>-</td>
    <td>No</td>
    </tr>
    <tr>
    <td>to</td>
    <td>to</td>
    <td>String</td>
    <td>Message to (optional)</td>
    <td>-</td>
    <td>No</td>
    </tr>
    <tr>
    <td>replyTo</td>
    <td>replyTo</td>
    <td>String</td>
    <td>Message reply to (optional)</td>
    <td>-</td>
    <td>No</td>
    </tr>
    <tr>
    <td>replyToSessionId</td>
    <td>replyToSessionId</td>
    <td>String</td>
    <td>Identifier of the session to reply to (optional)</td>
    <td>-</td>
    <td>No</td>
    </tr>
    <tr>
    <td>label</td>
    <td>label</td>
    <td>String</td>
    <td>Message label (optional)</td>
    <td>-</td>
    <td>No</td>
    </tr>
    <tr>
    <td>sessionId</td>
    <td>sessionId</td>
    <td>String</td>
    <td>Message session Id (optional)</td>
    <td>-</td>
    <td>No</td>
    </tr>
    <tr>
    <td>correlationId</td>
    <td>correlationId</td>
    <td>String</td>
    <td>Message correlationId (optional)</td>
    <td>-</td>
    <td>No</td>
    </tr>
    <tr>
    <td>partitionKey</td>
    <td>partitionKey</td>
    <td>String</td>
    <td>Message partition key (optional)</td>
    <td>-</td>
    <td>No</td>
    </tr>
    <tr>
    <td>timeToLive</td>
    <td>timeToLive</td>
    <td>String</td>
    <td>Message time to live in seconds (optional)</td>
    <td>-</td>
    <td>No</td>
    </tr>
    <tr>
    <td>sequenceNumber</td>
    <td>sequenceNumber</td>
    <td>String</td>
    <td>Message sequence number (optional)</td>
    <td>-</td>
    <td>No</td>
    </tr>
    <tr>
    <td>lockToken</td>
    <td>lockToken</td>
    <td>String</td>
    <td>Message lock token (optional)</td>
    <td>-</td>
    <td>No</td>
    </tr>
    <tr>
    <td>properties<br/><small>(Application Properties)</small></td>
    <td>applicationProperties_properties</td>
    <td>String</td>
    <td>Expecting JSON object with key-value pairs</td>
    <td>-</td>
    <td>No</td>
    </tr>
    <tr>
    <td>deliveryCount</td>
    <td>deliveryCount</td>
    <td>String</td>
    <td>Number of times a message has been delivered in a queue/subscription</td>
    <td>-</td>
    <td>No</td>
    </tr>
    <tr>
    <td>enqueuedTime</td>
    <td>enqueuedTime</td>
    <td>String</td>
    <td>Timestamp indicating when a message was added to the queue/subscription</td>
    <td>-</td>
    <td>No</td>
    </tr>
    <tr>
    <td>enqueuedSequenceNumber</td>
    <td>enqueuedSequenceNumber</td>
    <td>String</td>
    <td>Sequence number assigned to a message when it is added to the queue/subscription</td>
    <td>-</td>
    <td>No</td>
    </tr>
    <tr>
    <td>deadLetterErrorDescription</td>
    <td>deadLetterErrorDescription</td>
    <td>String</td>
    <td>The deadletter error description</td>
    <td>-</td>
    <td>No</td>
    </tr>
    <tr>
    <td>deadLetterReason</td>
    <td>deadLetterReason</td>
    <td>String</td>
    <td>The deadletter reason</td>
    <td>-</td>
    <td>No</td>
    </tr>
    <tr>
    <td>deadLetterSource</td>
    <td>deadLetterSource</td>
    <td>String</td>
    <td>Original queue/subscription where the message was before being moved to the dead-letter queue</td>
    <td>-</td>
    <td>No</td>
    </tr>
    <tr>
    <td>state</td>
    <td>state</td>
    <td>String</td>
    <td>Current state of a message in the queue/subscription, could be "Active", "Scheduled", "Deferred", etc.</td>
    <td>-</td>
    <td>No</td>
    </tr>
    <tr>
    <td>Output Variable Name</td>
    <td>responseVariable</td>
    <td>String</td>
    <td>The target variable in which the output of the operation will be stored</td>
    <td>-</td>
    <td>No</td>
    </tr>
    <tr>
    <td>Overwrite Message Body</td>
    <td>overwriteBody</td>
    <td>Boolean</td>
    <td>Replace the Message Body in Message Context with the output payload of the operation (This will remove the payload from the above variable. But other elements such as headers and attributes will remain).</td>
    <td>false</td>
    <td>No</td>
    </tr>
    </table>

    **Sample configuration**
    ```xml
    <asb.MessageReceiver_abandon configKey="CONNECTION_NAME">
        <body>{$ctx:body}</body>
        <responseVariable>asb_MessageReceiver_abandon_1</responseVariable>
        <overwriteBody>false</overwriteBody>
    </asb.MessageReceiver_abandon>
    ```

??? note "close"
    Closes the ASB receiver connection.
    ```ballerina
    check receiver->close();
    ```

    <table>
    <tr>
    <th>Parameter Name</th>
    <th>Element</th>
    <th>Type</th>
    <th>Description</th>
    <th>Default Value</th>
    <th>Required</th>
    </tr>
    <tr>
    <td>Output Variable Name</td>
    <td>responseVariable</td>
    <td>String</td>
    <td>The target variable in which the output of the operation will be stored</td>
    <td>-</td>
    <td>No</td>
    </tr>
    <tr>
    <td>Overwrite Message Body</td>
    <td>overwriteBody</td>
    <td>Boolean</td>
    <td>Replace the Message Body in Message Context with the output payload of the operation (This will remove the payload from the above variable. But other elements such as headers and attributes will remain).</td>
    <td>false</td>
    <td>No</td>
    </tr>
    </table>

    **Sample configuration**
    ```xml
    <asb.MessageReceiver_close configKey="CONNECTION_NAME">
        <responseVariable>asb_MessageReceiver_close_1</responseVariable>
        <overwriteBody>false</overwriteBody>
    </asb.MessageReceiver_close>
    ```

??? note "complete"
    Complete message from queue or subscription based on messageLockToken. Declares the message processing to be 
    successfully completed, removing the message from the queue.
    ```ballerina
    asb:Message message = ...;
    check receiver->complete(message);
    ```

    <table>
    <tr>
    <th>Parameter Name</th>
    <th>Element</th>
    <th>Type</th>
    <th>Description</th>
    <th>Default Value</th>
    <th>Required</th>
    </tr>
    <tr>
    <td>body</td>
    <td>body</td>
    <td>String</td>
    <td>Expecting JSON object</td>
    <td>-</td>
    <td>Yes</td>
    </tr>
    <tr>
    <td>contentType</td>
    <td>contentType</td>
    <td>String</td>
    <td>Message content type, with a descriptor following the format of `RFC2045`, (e.g. `application/json`) (optional)</td>
    <td>-</td>
    <td>No</td>
    </tr>
    <tr>
    <td>messageId</td>
    <td>messageId</td>
    <td>String</td>
    <td>Message Id (optional)</td>
    <td>-</td>
    <td>No</td>
    </tr>
    <tr>
    <td>to</td>
    <td>to</td>
    <td>String</td>
    <td>Message to (optional)</td>
    <td>-</td>
    <td>No</td>
    </tr>
    <tr>
    <td>replyTo</td>
    <td>replyTo</td>
    <td>String</td>
    <td>Message reply to (optional)</td>
    <td>-</td>
    <td>No</td>
    </tr>
    <tr>
    <td>replyToSessionId</td>
    <td>replyToSessionId</td>
    <td>String</td>
    <td>Identifier of the session to reply to (optional)</td>
    <td>-</td>
    <td>No</td>
    </tr>
    <tr>
    <td>label</td>
    <td>label</td>
    <td>String</td>
    <td>Message label (optional)</td>
    <td>-</td>
    <td>No</td>
    </tr>
    <tr>
    <td>sessionId</td>
    <td>sessionId</td>
    <td>String</td>
    <td>Message session Id (optional)</td>
    <td>-</td>
    <td>No</td>
    </tr>
    <tr>
    <td>correlationId</td>
    <td>correlationId</td>
    <td>String</td>
    <td>Message correlationId (optional)</td>
    <td>-</td>
    <td>No</td>
    </tr>
    <tr>
    <td>partitionKey</td>
    <td>partitionKey</td>
    <td>String</td>
    <td>Message partition key (optional)</td>
    <td>-</td>
    <td>No</td>
    </tr>
    <tr>
    <td>timeToLive</td>
    <td>timeToLive</td>
    <td>String</td>
    <td>Message time to live in seconds (optional)</td>
    <td>-</td>
    <td>No</td>
    </tr>
    <tr>
    <td>sequenceNumber</td>
    <td>sequenceNumber</td>
    <td>String</td>
    <td>Message sequence number (optional)</td>
    <td>-</td>
    <td>No</td>
    </tr>
    <tr>
    <td>lockToken</td>
    <td>lockToken</td>
    <td>String</td>
    <td>Message lock token (optional)</td>
    <td>-</td>
    <td>No</td>
    </tr>
    <tr>
    <td>properties<br/><small>(Application Properties)</small></td>
    <td>applicationProperties_properties</td>
    <td>String</td>
    <td>Expecting JSON object with key-value pairs</td>
    <td>-</td>
    <td>No</td>
    </tr>
    <tr>
    <td>deliveryCount</td>
    <td>deliveryCount</td>
    <td>String</td>
    <td>Number of times a message has been delivered in a queue/subscription</td>
    <td>-</td>
    <td>No</td>
    </tr>
    <tr>
    <td>enqueuedTime</td>
    <td>enqueuedTime</td>
    <td>String</td>
    <td>Timestamp indicating when a message was added to the queue/subscription</td>
    <td>-</td>
    <td>No</td>
    </tr>
    <tr>
    <td>enqueuedSequenceNumber</td>
    <td>enqueuedSequenceNumber</td>
    <td>String</td>
    <td>Sequence number assigned to a message when it is added to the queue/subscription</td>
    <td>-</td>
    <td>No</td>
    </tr>
    <tr>
    <td>deadLetterErrorDescription</td>
    <td>deadLetterErrorDescription</td>
    <td>String</td>
    <td>The deadletter error description</td>
    <td>-</td>
    <td>No</td>
    </tr>
    <tr>
    <td>deadLetterReason</td>
    <td>deadLetterReason</td>
    <td>String</td>
    <td>The deadletter reason</td>
    <td>-</td>
    <td>No</td>
    </tr>
    <tr>
    <td>deadLetterSource</td>
    <td>deadLetterSource</td>
    <td>String</td>
    <td>Original queue/subscription where the message was before being moved to the dead-letter queue</td>
    <td>-</td>
    <td>No</td>
    </tr>
    <tr>
    <td>state</td>
    <td>state</td>
    <td>String</td>
    <td>Current state of a message in the queue/subscription, could be "Active", "Scheduled", "Deferred", etc.</td>
    <td>-</td>
    <td>No</td>
    </tr>
    <tr>
    <td>Output Variable Name</td>
    <td>responseVariable</td>
    <td>String</td>
    <td>The target variable in which the output of the operation will be stored</td>
    <td>-</td>
    <td>No</td>
    </tr>
    <tr>
    <td>Overwrite Message Body</td>
    <td>overwriteBody</td>
    <td>Boolean</td>
    <td>Replace the Message Body in Message Context with the output payload of the operation (This will remove the payload from the above variable. But other elements such as headers and attributes will remain).</td>
    <td>false</td>
    <td>No</td>
    </tr>
    </table>

    **Sample configuration**
    ```xml
    <asb.MessageReceiver_complete configKey="CONNECTION_NAME">
        <body>{$ctx:body}</body>
        <responseVariable>asb_MessageReceiver_complete_1</responseVariable>
        <overwriteBody>false</overwriteBody>
    </asb.MessageReceiver_complete>
    ```

??? note "dead letter"
    Dead-Letter the message & moves the message to the Dead-Letter Queue based on messageLockToken. Transfer 
    the message from the primary queue into a special "dead-letter sub-queue".
    ```ballerina
    asb:Message message = ...;
    check receiver->deadLetter(message);
    ```

    <table>
    <tr>
    <th>Parameter Name</th>
    <th>Element</th>
    <th>Type</th>
    <th>Description</th>
    <th>Default Value</th>
    <th>Required</th>
    </tr>
    <tr>
    <td>body</td>
    <td>body</td>
    <td>String</td>
    <td>Expecting JSON object</td>
    <td>-</td>
    <td>Yes</td>
    </tr>
    <tr>
    <td>contentType</td>
    <td>contentType</td>
    <td>String</td>
    <td>Message content type, with a descriptor following the format of `RFC2045`, (e.g. `application/json`) (optional)</td>
    <td>-</td>
    <td>No</td>
    </tr>
    <tr>
    <td>messageId</td>
    <td>messageId</td>
    <td>String</td>
    <td>Message Id (optional)</td>
    <td>-</td>
    <td>No</td>
    </tr>
    <tr>
    <td>to</td>
    <td>to</td>
    <td>String</td>
    <td>Message to (optional)</td>
    <td>-</td>
    <td>No</td>
    </tr>
    <tr>
    <td>replyTo</td>
    <td>replyTo</td>
    <td>String</td>
    <td>Message reply to (optional)</td>
    <td>-</td>
    <td>No</td>
    </tr>
    <tr>
    <td>replyToSessionId</td>
    <td>replyToSessionId</td>
    <td>String</td>
    <td>Identifier of the session to reply to (optional)</td>
    <td>-</td>
    <td>No</td>
    </tr>
    <tr>
    <td>label</td>
    <td>label</td>
    <td>String</td>
    <td>Message label (optional)</td>
    <td>-</td>
    <td>No</td>
    </tr>
    <tr>
    <td>sessionId</td>
    <td>sessionId</td>
    <td>String</td>
    <td>Message session Id (optional)</td>
    <td>-</td>
    <td>No</td>
    </tr>
    <tr>
    <td>correlationId</td>
    <td>correlationId</td>
    <td>String</td>
    <td>Message correlationId (optional)</td>
    <td>-</td>
    <td>No</td>
    </tr>
    <tr>
    <td>partitionKey</td>
    <td>partitionKey</td>
    <td>String</td>
    <td>Message partition key (optional)</td>
    <td>-</td>
    <td>No</td>
    </tr>
    <tr>
    <td>timeToLive</td>
    <td>timeToLive</td>
    <td>String</td>
    <td>Message time to live in seconds (optional)</td>
    <td>-</td>
    <td>No</td>
    </tr>
    <tr>
    <td>sequenceNumber</td>
    <td>sequenceNumber</td>
    <td>String</td>
    <td>Message sequence number (optional)</td>
    <td>-</td>
    <td>No</td>
    </tr>
    <tr>
    <td>lockToken</td>
    <td>lockToken</td>
    <td>String</td>
    <td>Message lock token (optional)</td>
    <td>-</td>
    <td>No</td>
    </tr>
    <tr>
    <td>properties<br/><small>(Application Properties)</small></td>
    <td>applicationProperties_properties</td>
    <td>String</td>
    <td>Expecting JSON object with key-value pairs</td>
    <td>-</td>
    <td>No</td>
    </tr>
    <tr>
    <td>deliveryCount</td>
    <td>deliveryCount</td>
    <td>String</td>
    <td>Number of times a message has been delivered in a queue/subscription</td>
    <td>-</td>
    <td>No</td>
    </tr>
    <tr>
    <td>enqueuedTime</td>
    <td>enqueuedTime</td>
    <td>String</td>
    <td>Timestamp indicating when a message was added to the queue/subscription</td>
    <td>-</td>
    <td>No</td>
    </tr>
    <tr>
    <td>enqueuedSequenceNumber</td>
    <td>enqueuedSequenceNumber</td>
    <td>String</td>
    <td>Sequence number assigned to a message when it is added to the queue/subscription</td>
    <td>-</td>
    <td>No</td>
    </tr>
    <tr>
    <td>deadLetterErrorDescription</td>
    <td>deadLetterErrorDescription</td>
    <td>String</td>
    <td>The deadletter error description (optional)</td>
    <td>-</td>
    <td>No</td>
    </tr>
    <tr>
    <td>deadLetterReason</td>
    <td>deadLetterReason</td>
    <td>String</td>
    <td>The deadletter reason (optional)</td>
    <td>-</td>
    <td>No</td>
    </tr>
    <tr>
    <td>deadLetterSource</td>
    <td>deadLetterSource</td>
    <td>String</td>
    <td>Original queue/subscription where the message was before being moved to the dead-letter queue</td>
    <td>-</td>
    <td>No</td>
    </tr>
    <tr>
    <td>state</td>
    <td>state</td>
    <td>String</td>
    <td>Current state of a message in the queue/subscription, could be "Active", "Scheduled", "Deferred", etc.</td>
    <td>-</td>
    <td>No</td>
    </tr>
    <tr>
    <td>deadLetterReason<br/><small>(Advanced)</small></td>
    <td>deadLetterReason</td>
    <td>String</td>
    <td>The deadletter reason (optional)</td>
    <td>DEADLETTERED_BY_RECEIVER</td>
    <td>No</td>
    </tr>
    <tr>
    <td>deadLetterErrorDescription<br/><small>(Advanced)</small></td>
    <td>deadLetterErrorDescription</td>
    <td>String</td>
    <td>The deadletter error description (optional)</td>
    <td>-</td>
    <td>No</td>
    </tr>
    <tr>
    <td>Output Variable Name</td>
    <td>responseVariable</td>
    <td>String</td>
    <td>The target variable in which the output of the operation will be stored</td>
    <td>-</td>
    <td>No</td>
    </tr>
    <tr>
    <td>Overwrite Message Body</td>
    <td>overwriteBody</td>
    <td>Boolean</td>
    <td>Replace the Message Body in Message Context with the output payload of the operation (This will remove the payload from the above variable. But other elements such as headers and attributes will remain).</td>
    <td>false</td>
    <td>No</td>
    </tr>
    </table>

    **Sample configuration**
    ```xml
    <asb.MessageReceiver_deadLetter configKey="CONNECTION_NAME">
        <body>{$ctx:body}</body>
        <responseVariable>asb_MessageReceiver_deadLetter_1</responseVariable>
        <overwriteBody>false</overwriteBody>
    </asb.MessageReceiver_deadLetter>
    ```

??? note "defer"
    Defer the message in a Queue or Subscription based on messageLockToken.  It prevents the message from being 
    directly received from the queue by setting it aside such that it must be received by sequence number.
    ```ballerina
    asb:Message message = ...;
    int sequenceNumber = check receiver->defer(message);
    ```

    <table>
    <tr>
    <th>Parameter Name</th>
    <th>Element</th>
    <th>Type</th>
    <th>Description</th>
    <th>Default Value</th>
    <th>Required</th>
    </tr>
    <tr>
    <td>body</td>
    <td>body</td>
    <td>String</td>
    <td>Expecting JSON object</td>
    <td>-</td>
    <td>Yes</td>
    </tr>
    <tr>
    <td>contentType</td>
    <td>contentType</td>
    <td>String</td>
    <td>Message content type, with a descriptor following the format of `RFC2045`, (e.g. `application/json`) (optional)</td>
    <td>-</td>
    <td>No</td>
    </tr>
    <tr>
    <td>messageId</td>
    <td>messageId</td>
    <td>String</td>
    <td>Message Id (optional)</td>
    <td>-</td>
    <td>No</td>
    </tr>
    <tr>
    <td>to</td>
    <td>to</td>
    <td>String</td>
    <td>Message to (optional)</td>
    <td>-</td>
    <td>No</td>
    </tr>
    <tr>
    <td>replyTo</td>
    <td>replyTo</td>
    <td>String</td>
    <td>Message reply to (optional)</td>
    <td>-</td>
    <td>No</td>
    </tr>
    <tr>
    <td>replyToSessionId</td>
    <td>replyToSessionId</td>
    <td>String</td>
    <td>Identifier of the session to reply to (optional)</td>
    <td>-</td>
    <td>No</td>
    </tr>
    <tr>
    <td>label</td>
    <td>label</td>
    <td>String</td>
    <td>Message label (optional)</td>
    <td>-</td>
    <td>No</td>
    </tr>
    <tr>
    <td>sessionId</td>
    <td>sessionId</td>
    <td>String</td>
    <td>Message session Id (optional)</td>
    <td>-</td>
    <td>No</td>
    </tr>
    <tr>
    <td>correlationId</td>
    <td>correlationId</td>
    <td>String</td>
    <td>Message correlationId (optional)</td>
    <td>-</td>
    <td>No</td>
    </tr>
    <tr>
    <td>partitionKey</td>
    <td>partitionKey</td>
    <td>String</td>
    <td>Message partition key (optional)</td>
    <td>-</td>
    <td>No</td>
    </tr>
    <tr>
    <td>timeToLive</td>
    <td>timeToLive</td>
    <td>String</td>
    <td>Message time to live in seconds (optional)</td>
    <td>-</td>
    <td>No</td>
    </tr>
    <tr>
    <td>sequenceNumber</td>
    <td>sequenceNumber</td>
    <td>String</td>
    <td>Message sequence number (optional)</td>
    <td>-</td>
    <td>No</td>
    </tr>
    <tr>
    <td>lockToken</td>
    <td>lockToken</td>
    <td>String</td>
    <td>Message lock token (optional)</td>
    <td>-</td>
    <td>No</td>
    </tr>
    <tr>
    <td>properties<br/><small>(Application Properties)</small></td>
    <td>applicationProperties_properties</td>
    <td>String</td>
    <td>Expecting JSON object with key-value pairs</td>
    <td>-</td>
    <td>No</td>
    </tr>
    <tr>
    <td>deliveryCount</td>
    <td>deliveryCount</td>
    <td>String</td>
    <td>Number of times a message has been delivered in a queue/subscription</td>
    <td>-</td>
    <td>No</td>
    </tr>
    <tr>
    <td>enqueuedTime</td>
    <td>enqueuedTime</td>
    <td>String</td>
    <td>Timestamp indicating when a message was added to the queue/subscription</td>
    <td>-</td>
    <td>No</td>
    </tr>
    <tr>
    <td>enqueuedSequenceNumber</td>
    <td>enqueuedSequenceNumber</td>
    <td>String</td>
    <td>Sequence number assigned to a message when it is added to the queue/subscription</td>
    <td>-</td>
    <td>No</td>
    </tr>
    <tr>
    <td>deadLetterErrorDescription</td>
    <td>deadLetterErrorDescription</td>
    <td>String</td>
    <td>The deadletter error description</td>
    <td>-</td>
    <td>No</td>
    </tr>
    <tr>
    <td>deadLetterReason</td>
    <td>deadLetterReason</td>
    <td>String</td>
    <td>The deadletter reason</td>
    <td>-</td>
    <td>No</td>
    </tr>
    <tr>
    <td>deadLetterSource</td>
    <td>deadLetterSource</td>
    <td>String</td>
    <td>Original queue/subscription where the message was before being moved to the dead-letter queue</td>
    <td>-</td>
    <td>No</td>
    </tr>
    <tr>
    <td>state</td>
    <td>state</td>
    <td>String</td>
    <td>Current state of a message in the queue/subscription, could be "Active", "Scheduled", "Deferred", etc.</td>
    <td>-</td>
    <td>No</td>
    </tr>
    <tr>
    <td>Output Variable Name</td>
    <td>responseVariable</td>
    <td>String</td>
    <td>The target variable in which the output of the operation will be stored</td>
    <td>-</td>
    <td>No</td>
    </tr>
    <tr>
    <td>Overwrite Message Body</td>
    <td>overwriteBody</td>
    <td>Boolean</td>
    <td>Replace the Message Body in Message Context with the output payload of the operation (This will remove the payload from the above variable. But other elements such as headers and attributes will remain).</td>
    <td>false</td>
    <td>No</td>
    </tr>
    </table>

    **Sample configuration**
    ```xml
    <asb.MessageReceiver_defer configKey="CONNECTION_NAME">
        <body>{$ctx:body}</body>
        <responseVariable>asb_MessageReceiver_defer_1</responseVariable>
        <overwriteBody>false</overwriteBody>
    </asb.MessageReceiver_defer>
    ```

??? note "receive"
    Receive message from queue or subscription.
    ```ballerina
    asb:Message? message = check receiver->receive();
    ```

    <table>
    <tr>
    <th>Parameter Name</th>
    <th>Element</th>
    <th>Type</th>
    <th>Description</th>
    <th>Default Value</th>
    <th>Required</th>
    </tr>
    <tr>
    <td>serverWaitTime<br/><small>(Advanced)</small></td>
    <td>serverWaitTime</td>
    <td>String</td>
    <td>Specified server wait time in seconds to receive message (optional)</td>
    <td>60</td>
    <td>No</td>
    </tr>
    <tr>
    <td>deadLettered<br/><small>(Advanced)</small></td>
    <td>deadLettered</td>
    <td>Boolean</td>
    <td>If set to `true`, messages from dead-letter queue will be received. (optional)</td>
    <td>false</td>
    <td>No</td>
    </tr>
    <tr>
    <td>Output Variable Name</td>
    <td>responseVariable</td>
    <td>String</td>
    <td>The target variable in which the output of the operation will be stored</td>
    <td>-</td>
    <td>No</td>
    </tr>
    <tr>
    <td>Overwrite Message Body</td>
    <td>overwriteBody</td>
    <td>Boolean</td>
    <td>Replace the Message Body in Message Context with the output payload of the operation (This will remove the payload from the above variable. But other elements such as headers and attributes will remain).</td>
    <td>false</td>
    <td>No</td>
    </tr>
    </table>

    **Sample configuration**
    ```xml
    <asb.MessageReceiver_receive configKey="CONNECTION_NAME">
        <responseVariable>asb_MessageReceiver_receive_1</responseVariable>
        <overwriteBody>false</overwriteBody>
    </asb.MessageReceiver_receive>
    ```

??? note "receive batch"
    Receive batch of messages from queue or subscription.
    ```ballerina
    asb:MessageBatch batch = check receiver->receiveBatch(10);
    ```

    <table>
    <tr>
    <th>Parameter Name</th>
    <th>Element</th>
    <th>Type</th>
    <th>Description</th>
    <th>Default Value</th>
    <th>Required</th>
    </tr>
    <tr>
    <td>maxMessageCount</td>
    <td>maxMessageCount</td>
    <td>String</td>
    <td>Maximum message count to receive in a batch</td>
    <td>-</td>
    <td>Yes</td>
    </tr>
    <tr>
    <td>serverWaitTime<br/><small>(Advanced)</small></td>
    <td>serverWaitTime</td>
    <td>String</td>
    <td>Specified server wait time in seconds to receive message (optional)</td>
    <td>-</td>
    <td>No</td>
    </tr>
    <tr>
    <td>deadLettered<br/><small>(Advanced)</small></td>
    <td>deadLettered</td>
    <td>Boolean</td>
    <td>If set to `true`, messages from dead-letter queue will be received. (optional)</td>
    <td>false</td>
    <td>No</td>
    </tr>
    <tr>
    <td>Output Variable Name</td>
    <td>responseVariable</td>
    <td>String</td>
    <td>The target variable in which the output of the operation will be stored</td>
    <td>-</td>
    <td>No</td>
    </tr>
    <tr>
    <td>Overwrite Message Body</td>
    <td>overwriteBody</td>
    <td>Boolean</td>
    <td>Replace the Message Body in Message Context with the output payload of the operation (This will remove the payload from the above variable. But other elements such as headers and attributes will remain).</td>
    <td>false</td>
    <td>No</td>
    </tr>
    </table>

    **Sample configuration**
    ```xml
    <asb.MessageReceiver_receiveBatch configKey="CONNECTION_NAME">
        <maxMessageCount>{$ctx:maxMessageCount}</maxMessageCount>
        <responseVariable>asb_MessageReceiver_receiveBatch_1</responseVariable>
        <overwriteBody>false</overwriteBody>
    </asb.MessageReceiver_receiveBatch>
    ```

??? note "receive deferred"
    Receives a deferred Message. Deferred messages can only be received by using sequence number and return
    Message object.
    ```ballerina
    asb:Message? message = check receiver->receiveDeferred(1);
    ```

    <table>
    <tr>
    <th>Parameter Name</th>
    <th>Element</th>
    <th>Type</th>
    <th>Description</th>
    <th>Default Value</th>
    <th>Required</th>
    </tr>
    <tr>
    <td>sequenceNumber</td>
    <td>sequenceNumber</td>
    <td>String</td>
    <td>Unique number assigned to a message by Service Bus. The sequence number is a unique 64-bit
    integer assigned to a message as it is accepted and stored by the broker and functions as
    its true identifier.</td>
    <td>-</td>
    <td>Yes</td>
    </tr>
    <tr>
    <td>Output Variable Name</td>
    <td>responseVariable</td>
    <td>String</td>
    <td>The target variable in which the output of the operation will be stored</td>
    <td>-</td>
    <td>No</td>
    </tr>
    <tr>
    <td>Overwrite Message Body</td>
    <td>overwriteBody</td>
    <td>Boolean</td>
    <td>Replace the Message Body in Message Context with the output payload of the operation (This will remove the payload from the above variable. But other elements such as headers and attributes will remain).</td>
    <td>false</td>
    <td>No</td>
    </tr>
    </table>

    **Sample configuration**
    ```xml
    <asb.MessageReceiver_receiveDeferred configKey="CONNECTION_NAME">
        <sequenceNumber>{$ctx:sequenceNumber}</sequenceNumber>
        <responseVariable>asb_MessageReceiver_receiveDeferred_1</responseVariable>
        <overwriteBody>false</overwriteBody>
    </asb.MessageReceiver_receiveDeferred>
    ```

??? note "receive payload"
    Receive message payload from queue or subscription.
    ```ballerina
    string messagePayload = check receiver->receivePayload();
    ```

    <table>
    <tr>
    <th>Parameter Name</th>
    <th>Element</th>
    <th>Type</th>
    <th>Description</th>
    <th>Default Value</th>
    <th>Required</th>
    </tr>
    <tr>
    <td>serverWaitTime<br/><small>(Advanced)</small></td>
    <td>serverWaitTime</td>
    <td>String</td>
    <td>Specified server wait time in seconds to receive message (optional)</td>
    <td>60</td>
    <td>No</td>
    </tr>
    <tr>
    <td>deadLettered<br/><small>(Advanced)</small></td>
    <td>deadLettered</td>
    <td>Boolean</td>
    <td>If set to `true`, messages from dead-letter queue will be received. (optional)</td>
    <td>false</td>
    <td>No</td>
    </tr>
    <tr>
    <td>Output Variable Name</td>
    <td>responseVariable</td>
    <td>String</td>
    <td>The target variable in which the output of the operation will be stored</td>
    <td>-</td>
    <td>No</td>
    </tr>
    <tr>
    <td>Overwrite Message Body</td>
    <td>overwriteBody</td>
    <td>Boolean</td>
    <td>Replace the Message Body in Message Context with the output payload of the operation (This will remove the payload from the above variable. But other elements such as headers and attributes will remain).</td>
    <td>false</td>
    <td>No</td>
    </tr>
    </table>

    **Sample configuration**
    ```xml
    <asb.MessageReceiver_receivePayload configKey="CONNECTION_NAME">
        <responseVariable>asb_MessageReceiver_receivePayload_1</responseVariable>
        <overwriteBody>false</overwriteBody>
    </asb.MessageReceiver_receivePayload>
    ```

??? note "renew lock"
    The operation renews lock on a message in a queue or subscription based on messageLockToken.
    ```ballerina
    asb:Message message = ...;
    check receiver->renewLock(message);
    ```

    <table>
    <tr>
    <th>Parameter Name</th>
    <th>Element</th>
    <th>Type</th>
    <th>Description</th>
    <th>Default Value</th>
    <th>Required</th>
    </tr>
    <tr>
    <td>body</td>
    <td>body</td>
    <td>String</td>
    <td>Expecting JSON object</td>
    <td>-</td>
    <td>Yes</td>
    </tr>
    <tr>
    <td>contentType</td>
    <td>contentType</td>
    <td>String</td>
    <td>Message content type, with a descriptor following the format of `RFC2045`, (e.g. `application/json`) (optional)</td>
    <td>-</td>
    <td>No</td>
    </tr>
    <tr>
    <td>messageId</td>
    <td>messageId</td>
    <td>String</td>
    <td>Message Id (optional)</td>
    <td>-</td>
    <td>No</td>
    </tr>
    <tr>
    <td>to</td>
    <td>to</td>
    <td>String</td>
    <td>Message to (optional)</td>
    <td>-</td>
    <td>No</td>
    </tr>
    <tr>
    <td>replyTo</td>
    <td>replyTo</td>
    <td>String</td>
    <td>Message reply to (optional)</td>
    <td>-</td>
    <td>No</td>
    </tr>
    <tr>
    <td>replyToSessionId</td>
    <td>replyToSessionId</td>
    <td>String</td>
    <td>Identifier of the session to reply to (optional)</td>
    <td>-</td>
    <td>No</td>
    </tr>
    <tr>
    <td>label</td>
    <td>label</td>
    <td>String</td>
    <td>Message label (optional)</td>
    <td>-</td>
    <td>No</td>
    </tr>
    <tr>
    <td>sessionId</td>
    <td>sessionId</td>
    <td>String</td>
    <td>Message session Id (optional)</td>
    <td>-</td>
    <td>No</td>
    </tr>
    <tr>
    <td>correlationId</td>
    <td>correlationId</td>
    <td>String</td>
    <td>Message correlationId (optional)</td>
    <td>-</td>
    <td>No</td>
    </tr>
    <tr>
    <td>partitionKey</td>
    <td>partitionKey</td>
    <td>String</td>
    <td>Message partition key (optional)</td>
    <td>-</td>
    <td>No</td>
    </tr>
    <tr>
    <td>timeToLive</td>
    <td>timeToLive</td>
    <td>String</td>
    <td>Message time to live in seconds (optional)</td>
    <td>-</td>
    <td>No</td>
    </tr>
    <tr>
    <td>sequenceNumber</td>
    <td>sequenceNumber</td>
    <td>String</td>
    <td>Message sequence number (optional)</td>
    <td>-</td>
    <td>No</td>
    </tr>
    <tr>
    <td>lockToken</td>
    <td>lockToken</td>
    <td>String</td>
    <td>Message lock token (optional)</td>
    <td>-</td>
    <td>No</td>
    </tr>
    <tr>
    <td>properties<br/><small>(Application Properties)</small></td>
    <td>applicationProperties_properties</td>
    <td>String</td>
    <td>Expecting JSON object with key-value pairs</td>
    <td>-</td>
    <td>No</td>
    </tr>
    <tr>
    <td>deliveryCount</td>
    <td>deliveryCount</td>
    <td>String</td>
    <td>Number of times a message has been delivered in a queue/subscription</td>
    <td>-</td>
    <td>No</td>
    </tr>
    <tr>
    <td>enqueuedTime</td>
    <td>enqueuedTime</td>
    <td>String</td>
    <td>Timestamp indicating when a message was added to the queue/subscription</td>
    <td>-</td>
    <td>No</td>
    </tr>
    <tr>
    <td>enqueuedSequenceNumber</td>
    <td>enqueuedSequenceNumber</td>
    <td>String</td>
    <td>Sequence number assigned to a message when it is added to the queue/subscription</td>
    <td>-</td>
    <td>No</td>
    </tr>
    <tr>
    <td>deadLetterErrorDescription</td>
    <td>deadLetterErrorDescription</td>
    <td>String</td>
    <td>The deadletter error description</td>
    <td>-</td>
    <td>No</td>
    </tr>
    <tr>
    <td>deadLetterReason</td>
    <td>deadLetterReason</td>
    <td>String</td>
    <td>The deadletter reason</td>
    <td>-</td>
    <td>No</td>
    </tr>
    <tr>
    <td>deadLetterSource</td>
    <td>deadLetterSource</td>
    <td>String</td>
    <td>Original queue/subscription where the message was before being moved to the dead-letter queue</td>
    <td>-</td>
    <td>No</td>
    </tr>
    <tr>
    <td>state</td>
    <td>state</td>
    <td>String</td>
    <td>Current state of a message in the queue/subscription, could be "Active", "Scheduled", "Deferred", etc.</td>
    <td>-</td>
    <td>No</td>
    </tr>
    <tr>
    <td>Output Variable Name</td>
    <td>responseVariable</td>
    <td>String</td>
    <td>The target variable in which the output of the operation will be stored</td>
    <td>-</td>
    <td>No</td>
    </tr>
    <tr>
    <td>Overwrite Message Body</td>
    <td>overwriteBody</td>
    <td>Boolean</td>
    <td>Replace the Message Body in Message Context with the output payload of the operation (This will remove the payload from the above variable. But other elements such as headers and attributes will remain).</td>
    <td>false</td>
    <td>No</td>
    </tr>
    </table>

    **Sample configuration**
    ```xml
    <asb.MessageReceiver_renewLock configKey="CONNECTION_NAME">
        <body>{$ctx:body}</body>
        <responseVariable>asb_MessageReceiver_renewLock_1</responseVariable>
        <overwriteBody>false</overwriteBody>
    </asb.MessageReceiver_renewLock>
    ```

### MessageSender

??? note "cancel"
    Cancels the enqueuing of a scheduled message, if they are not already enqueued.
    ```ballerina
    check sender->cancel(1);
    ```

    <table>
    <tr>
    <th>Parameter Name</th>
    <th>Element</th>
    <th>Type</th>
    <th>Description</th>
    <th>Default Value</th>
    <th>Required</th>
    </tr>
    <tr>
    <td>sequenceNumber</td>
    <td>sequenceNumber</td>
    <td>String</td>
    <td>The sequence number of the message to cancel</td>
    <td>-</td>
    <td>Yes</td>
    </tr>
    <tr>
    <td>Output Variable Name</td>
    <td>responseVariable</td>
    <td>String</td>
    <td>The target variable in which the output of the operation will be stored</td>
    <td>-</td>
    <td>No</td>
    </tr>
    <tr>
    <td>Overwrite Message Body</td>
    <td>overwriteBody</td>
    <td>Boolean</td>
    <td>Replace the Message Body in Message Context with the output payload of the operation (This will remove the payload from the above variable. But other elements such as headers and attributes will remain).</td>
    <td>false</td>
    <td>No</td>
    </tr>
    </table>

    **Sample configuration**
    ```xml
    <asb.MessageSender_cancel configKey="CONNECTION_NAME">
        <sequenceNumber>{$ctx:sequenceNumber}</sequenceNumber>
        <responseVariable>asb_MessageSender_cancel_1</responseVariable>
        <overwriteBody>false</overwriteBody>
    </asb.MessageSender_cancel>
    ```

??? note "close"
    Closes the ASB sender connection.
    ```ballerina
    check sender->close();
    ```

    <table>
    <tr>
    <th>Parameter Name</th>
    <th>Element</th>
    <th>Type</th>
    <th>Description</th>
    <th>Default Value</th>
    <th>Required</th>
    </tr>
    <tr>
    <td>Output Variable Name</td>
    <td>responseVariable</td>
    <td>String</td>
    <td>The target variable in which the output of the operation will be stored</td>
    <td>-</td>
    <td>No</td>
    </tr>
    <tr>
    <td>Overwrite Message Body</td>
    <td>overwriteBody</td>
    <td>Boolean</td>
    <td>Replace the Message Body in Message Context with the output payload of the operation (This will remove the payload from the above variable. But other elements such as headers and attributes will remain).</td>
    <td>false</td>
    <td>No</td>
    </tr>
    </table>

    **Sample configuration**
    ```xml
    <asb.MessageSender_close configKey="CONNECTION_NAME">
        <responseVariable>asb_MessageSender_close_1</responseVariable>
        <overwriteBody>false</overwriteBody>
    </asb.MessageSender_close>
    ```

??? note "schedule"
    Sends a scheduled message to the Azure Service Bus entity this sender is connected to. 
    A scheduled message is enqueued and made available to receivers only at the scheduled enqueue time.
    ```ballerina
    time:Civil scheduledTime = check time:civilFromString("2007-12-03T10:15:30.00Z");
    check sender->send({body: "Sample text message", contentType: asb:TEXT}, scheduledTime);
    ```

    <table>
    <tr>
    <th>Parameter Name</th>
    <th>Element</th>
    <th>Type</th>
    <th>Description</th>
    <th>Default Value</th>
    <th>Required</th>
    </tr>
    <tr>
    <td>body</td>
    <td>body</td>
    <td>String</td>
    <td>Expecting JSON object</td>
    <td>-</td>
    <td>Yes</td>
    </tr>
    <tr>
    <td>contentType</td>
    <td>contentType</td>
    <td>String</td>
    <td>Message content type, with a descriptor following the format of `RFC2045`, (e.g. `application/json`) (optional)</td>
    <td>-</td>
    <td>No</td>
    </tr>
    <tr>
    <td>messageId</td>
    <td>messageId</td>
    <td>String</td>
    <td>Message Id (optional)</td>
    <td>-</td>
    <td>No</td>
    </tr>
    <tr>
    <td>to</td>
    <td>to</td>
    <td>String</td>
    <td>Message to (optional)</td>
    <td>-</td>
    <td>No</td>
    </tr>
    <tr>
    <td>replyTo</td>
    <td>replyTo</td>
    <td>String</td>
    <td>Message reply to (optional)</td>
    <td>-</td>
    <td>No</td>
    </tr>
    <tr>
    <td>replyToSessionId</td>
    <td>replyToSessionId</td>
    <td>String</td>
    <td>Identifier of the session to reply to (optional)</td>
    <td>-</td>
    <td>No</td>
    </tr>
    <tr>
    <td>label</td>
    <td>label</td>
    <td>String</td>
    <td>Message label (optional)</td>
    <td>-</td>
    <td>No</td>
    </tr>
    <tr>
    <td>sessionId</td>
    <td>sessionId</td>
    <td>String</td>
    <td>Message session Id (optional)</td>
    <td>-</td>
    <td>No</td>
    </tr>
    <tr>
    <td>correlationId</td>
    <td>correlationId</td>
    <td>String</td>
    <td>Message correlationId (optional)</td>
    <td>-</td>
    <td>No</td>
    </tr>
    <tr>
    <td>partitionKey</td>
    <td>partitionKey</td>
    <td>String</td>
    <td>Message partition key (optional)</td>
    <td>-</td>
    <td>No</td>
    </tr>
    <tr>
    <td>timeToLive</td>
    <td>timeToLive</td>
    <td>String</td>
    <td>Message time to live in seconds (optional)</td>
    <td>-</td>
    <td>No</td>
    </tr>
    <tr>
    <td>sequenceNumber</td>
    <td>sequenceNumber</td>
    <td>String</td>
    <td>Message sequence number (optional)</td>
    <td>-</td>
    <td>No</td>
    </tr>
    <tr>
    <td>lockToken</td>
    <td>lockToken</td>
    <td>String</td>
    <td>Message lock token (optional)</td>
    <td>-</td>
    <td>No</td>
    </tr>
    <tr>
    <td>properties<br/><small>(Application Properties)</small></td>
    <td>applicationProperties_properties</td>
    <td>String</td>
    <td>Expecting JSON object with key-value pairs</td>
    <td>-</td>
    <td>No</td>
    </tr>
    <tr>
    <td>deliveryCount</td>
    <td>deliveryCount</td>
    <td>String</td>
    <td>Number of times a message has been delivered in a queue/subscription</td>
    <td>-</td>
    <td>No</td>
    </tr>
    <tr>
    <td>enqueuedTime</td>
    <td>enqueuedTime</td>
    <td>String</td>
    <td>Timestamp indicating when a message was added to the queue/subscription</td>
    <td>-</td>
    <td>No</td>
    </tr>
    <tr>
    <td>enqueuedSequenceNumber</td>
    <td>enqueuedSequenceNumber</td>
    <td>String</td>
    <td>Sequence number assigned to a message when it is added to the queue/subscription</td>
    <td>-</td>
    <td>No</td>
    </tr>
    <tr>
    <td>deadLetterErrorDescription</td>
    <td>deadLetterErrorDescription</td>
    <td>String</td>
    <td>The deadletter error description</td>
    <td>-</td>
    <td>No</td>
    </tr>
    <tr>
    <td>deadLetterReason</td>
    <td>deadLetterReason</td>
    <td>String</td>
    <td>The deadletter reason</td>
    <td>-</td>
    <td>No</td>
    </tr>
    <tr>
    <td>deadLetterSource</td>
    <td>deadLetterSource</td>
    <td>String</td>
    <td>Original queue/subscription where the message was before being moved to the dead-letter queue</td>
    <td>-</td>
    <td>No</td>
    </tr>
    <tr>
    <td>state</td>
    <td>state</td>
    <td>String</td>
    <td>Current state of a message in the queue/subscription, could be "Active", "Scheduled", "Deferred", etc.</td>
    <td>-</td>
    <td>No</td>
    </tr>
    <tr>
    <td>timeAbbrev</td>
    <td>timeAbbrev</td>
    <td>String</td>
    <td>-</td>
    <td>-</td>
    <td>No</td>
    </tr>
    <tr>
    <td>which</td>
    <td>which</td>
    <td>Enum</td>
    <td><b>Possible values</b>: <code>0</code>, <code>1</code></td>
    <td>0</td>
    <td>No</td>
    </tr>
    <tr>
    <td>dayOfWeek</td>
    <td>dayOfWeek</td>
    <td>Enum</td>
    <td><b>Possible values</b>: <code>0</code>, <code>1</code>, <code>2</code>, <code>3</code>, <code>4</code>, <code>5</code>, <code>6</code></td>
    <td>0</td>
    <td>No</td>
    </tr>
    <tr>
    <td>year</td>
    <td>year</td>
    <td>String</td>
    <td>-</td>
    <td>-</td>
    <td>Yes</td>
    </tr>
    <tr>
    <td>month</td>
    <td>month</td>
    <td>String</td>
    <td>-</td>
    <td>-</td>
    <td>Yes</td>
    </tr>
    <tr>
    <td>day</td>
    <td>day</td>
    <td>String</td>
    <td>-</td>
    <td>-</td>
    <td>Yes</td>
    </tr>
    <tr>
    <td>hour</td>
    <td>hour</td>
    <td>String</td>
    <td>-</td>
    <td>-</td>
    <td>Yes</td>
    </tr>
    <tr>
    <td>minute</td>
    <td>minute</td>
    <td>String</td>
    <td>-</td>
    <td>-</td>
    <td>Yes</td>
    </tr>
    <tr>
    <td>second</td>
    <td>second</td>
    <td>String</td>
    <td>-</td>
    <td>-</td>
    <td>No</td>
    </tr>
    <tr>
    <td>Output Variable Name</td>
    <td>responseVariable</td>
    <td>String</td>
    <td>The target variable in which the output of the operation will be stored</td>
    <td>-</td>
    <td>No</td>
    </tr>
    <tr>
    <td>Overwrite Message Body</td>
    <td>overwriteBody</td>
    <td>Boolean</td>
    <td>Replace the Message Body in Message Context with the output payload of the operation (This will remove the payload from the above variable. But other elements such as headers and attributes will remain).</td>
    <td>false</td>
    <td>No</td>
    </tr>
    </table>

    **Sample configuration**
    ```xml
    <asb.MessageSender_schedule configKey="CONNECTION_NAME">
        <body>{$ctx:body}</body>
        <which>{$ctx:which}</which>
        <dayOfWeek>{$ctx:dayOfWeek}</dayOfWeek>
        <year>{$ctx:year}</year>
        <month>{$ctx:month}</month>
        <day>{$ctx:day}</day>
        <hour>{$ctx:hour}</hour>
        <minute>{$ctx:minute}</minute>
        <responseVariable>asb_MessageSender_schedule_1</responseVariable>
        <overwriteBody>false</overwriteBody>
    </asb.MessageSender_schedule>
    ```

??? note "send"
    Send message to queue or topic with a message body.
    ```ballerina
    check sender->send({body: "Sample text message", contentType: asb:TEXT});
    ```

    <table>
    <tr>
    <th>Parameter Name</th>
    <th>Element</th>
    <th>Type</th>
    <th>Description</th>
    <th>Default Value</th>
    <th>Required</th>
    </tr>
    <tr>
    <td>body</td>
    <td>body</td>
    <td>String</td>
    <td>Expecting JSON object</td>
    <td>-</td>
    <td>Yes</td>
    </tr>
    <tr>
    <td>contentType</td>
    <td>contentType</td>
    <td>String</td>
    <td>Message content type, with a descriptor following the format of `RFC2045`, (e.g. `application/json`) (optional)</td>
    <td>-</td>
    <td>No</td>
    </tr>
    <tr>
    <td>messageId</td>
    <td>messageId</td>
    <td>String</td>
    <td>Message Id (optional)</td>
    <td>-</td>
    <td>No</td>
    </tr>
    <tr>
    <td>to</td>
    <td>to</td>
    <td>String</td>
    <td>Message to (optional)</td>
    <td>-</td>
    <td>No</td>
    </tr>
    <tr>
    <td>replyTo</td>
    <td>replyTo</td>
    <td>String</td>
    <td>Message reply to (optional)</td>
    <td>-</td>
    <td>No</td>
    </tr>
    <tr>
    <td>replyToSessionId</td>
    <td>replyToSessionId</td>
    <td>String</td>
    <td>Identifier of the session to reply to (optional)</td>
    <td>-</td>
    <td>No</td>
    </tr>
    <tr>
    <td>label</td>
    <td>label</td>
    <td>String</td>
    <td>Message label (optional)</td>
    <td>-</td>
    <td>No</td>
    </tr>
    <tr>
    <td>sessionId</td>
    <td>sessionId</td>
    <td>String</td>
    <td>Message session Id (optional)</td>
    <td>-</td>
    <td>No</td>
    </tr>
    <tr>
    <td>correlationId</td>
    <td>correlationId</td>
    <td>String</td>
    <td>Message correlationId (optional)</td>
    <td>-</td>
    <td>No</td>
    </tr>
    <tr>
    <td>partitionKey</td>
    <td>partitionKey</td>
    <td>String</td>
    <td>Message partition key (optional)</td>
    <td>-</td>
    <td>No</td>
    </tr>
    <tr>
    <td>timeToLive</td>
    <td>timeToLive</td>
    <td>String</td>
    <td>Message time to live in seconds (optional)</td>
    <td>-</td>
    <td>No</td>
    </tr>
    <tr>
    <td>sequenceNumber</td>
    <td>sequenceNumber</td>
    <td>String</td>
    <td>Message sequence number (optional)</td>
    <td>-</td>
    <td>No</td>
    </tr>
    <tr>
    <td>lockToken</td>
    <td>lockToken</td>
    <td>String</td>
    <td>Message lock token (optional)</td>
    <td>-</td>
    <td>No</td>
    </tr>
    <tr>
    <td>properties<br/><small>(Application Properties)</small></td>
    <td>applicationProperties_properties</td>
    <td>String</td>
    <td>Expecting JSON object with key-value pairs</td>
    <td>-</td>
    <td>No</td>
    </tr>
    <tr>
    <td>deliveryCount</td>
    <td>deliveryCount</td>
    <td>String</td>
    <td>Number of times a message has been delivered in a queue/subscription</td>
    <td>-</td>
    <td>No</td>
    </tr>
    <tr>
    <td>enqueuedTime</td>
    <td>enqueuedTime</td>
    <td>String</td>
    <td>Timestamp indicating when a message was added to the queue/subscription</td>
    <td>-</td>
    <td>No</td>
    </tr>
    <tr>
    <td>enqueuedSequenceNumber</td>
    <td>enqueuedSequenceNumber</td>
    <td>String</td>
    <td>Sequence number assigned to a message when it is added to the queue/subscription</td>
    <td>-</td>
    <td>No</td>
    </tr>
    <tr>
    <td>deadLetterErrorDescription</td>
    <td>deadLetterErrorDescription</td>
    <td>String</td>
    <td>The deadletter error description</td>
    <td>-</td>
    <td>No</td>
    </tr>
    <tr>
    <td>deadLetterReason</td>
    <td>deadLetterReason</td>
    <td>String</td>
    <td>The deadletter reason</td>
    <td>-</td>
    <td>No</td>
    </tr>
    <tr>
    <td>deadLetterSource</td>
    <td>deadLetterSource</td>
    <td>String</td>
    <td>Original queue/subscription where the message was before being moved to the dead-letter queue</td>
    <td>-</td>
    <td>No</td>
    </tr>
    <tr>
    <td>state</td>
    <td>state</td>
    <td>String</td>
    <td>Current state of a message in the queue/subscription, could be "Active", "Scheduled", "Deferred", etc.</td>
    <td>-</td>
    <td>No</td>
    </tr>
    <tr>
    <td>Output Variable Name</td>
    <td>responseVariable</td>
    <td>String</td>
    <td>The target variable in which the output of the operation will be stored</td>
    <td>-</td>
    <td>No</td>
    </tr>
    <tr>
    <td>Overwrite Message Body</td>
    <td>overwriteBody</td>
    <td>Boolean</td>
    <td>Replace the Message Body in Message Context with the output payload of the operation (This will remove the payload from the above variable. But other elements such as headers and attributes will remain).</td>
    <td>false</td>
    <td>No</td>
    </tr>
    </table>

    **Sample configuration**
    ```xml
    <asb.MessageSender_send configKey="CONNECTION_NAME">
        <body>{$ctx:body}</body>
        <responseVariable>asb_MessageSender_send_1</responseVariable>
        <overwriteBody>false</overwriteBody>
    </asb.MessageSender_send>
    ```

??? note "send batch"
    Send batch of messages to queue or topic.
    ```ballerina
    asb:MessageBatch batch = ...;
    check sender->sendBatch(batch);
    ```

    <table>
    <tr>
    <th>Parameter Name</th>
    <th>Element</th>
    <th>Type</th>
    <th>Description</th>
    <th>Default Value</th>
    <th>Required</th>
    </tr>
    <tr>
    <td>messageCount</td>
    <td>messageCount</td>
    <td>String</td>
    <td>Number of messages in a batch</td>
    <td>-</td>
    <td>No</td>
    </tr>
    <tr>
    <td>Output Variable Name</td>
    <td>responseVariable</td>
    <td>String</td>
    <td>The target variable in which the output of the operation will be stored</td>
    <td>-</td>
    <td>No</td>
    </tr>
    <tr>
    <td>Overwrite Message Body</td>
    <td>overwriteBody</td>
    <td>Boolean</td>
    <td>Replace the Message Body in Message Context with the output payload of the operation (This will remove the payload from the above variable. But other elements such as headers and attributes will remain).</td>
    <td>false</td>
    <td>No</td>
    </tr>
    </table>

    **Sample configuration**
    ```xml
    <asb.MessageSender_sendBatch configKey="CONNECTION_NAME">
        <responseVariable>asb_MessageSender_sendBatch_1</responseVariable>
        <overwriteBody>false</overwriteBody>
    </asb.MessageSender_sendBatch>
    ```

??? note "send payload"
    Send message to queue or topic with a message body.
    ```ballerina
    check sender->sendPayload("Sample text message");
    ```

    <table>
    <tr>
    <th>Parameter Name</th>
    <th>Element</th>
    <th>Type</th>
    <th>Description</th>
    <th>Default Value</th>
    <th>Required</th>
    </tr>
    <tr>
    <td>messagePayload</td>
    <td>messagePayload</td>
    <td>String</td>
    <td>Expecting JSON object</td>
    <td>-</td>
    <td>Yes</td>
    </tr>
    <tr>
    <td>Output Variable Name</td>
    <td>responseVariable</td>
    <td>String</td>
    <td>The target variable in which the output of the operation will be stored</td>
    <td>-</td>
    <td>No</td>
    </tr>
    <tr>
    <td>Overwrite Message Body</td>
    <td>overwriteBody</td>
    <td>Boolean</td>
    <td>Replace the Message Body in Message Context with the output payload of the operation (This will remove the payload from the above variable. But other elements such as headers and attributes will remain).</td>
    <td>false</td>
    <td>No</td>
    </tr>
    </table>

    **Sample configuration**
    ```xml
    <asb.MessageSender_sendPayload configKey="CONNECTION_NAME">
        <messagePayload>{$ctx:messagePayload}</messagePayload>
        <responseVariable>asb_MessageSender_sendPayload_1</responseVariable>
        <overwriteBody>false</overwriteBody>
    </asb.MessageSender_sendPayload>
    ```
