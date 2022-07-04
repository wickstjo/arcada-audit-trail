- Strictly refusing to use relatively sensitive data such as coordinates is extremely restrictive, and often greatly reduces the quality of experience of a service.

- Arguably, the underlying issue isn't that situational usage of sensitive data, but rather the storage of it
and potential future leaks.

-------------------------------------------------------------------------------

- Building vast VPN tunnels in an attempt to secure IOT communication is messy and futile in many ways.

- To efficiently control the devices through APIs can also dangerous and complicated, particularly if you want to control and command a multitude of devices at once.

- Smart contracts offer a multi-dimensional solution for such an ordeal.
    - Built in encryption keys for authentication and masking data that enhances machine-to-machine communications.
    - Protected webhook like utility for sensitive orders.

- Majority of payload exchange should be machine-to-machine, and done via some async communication.
- Verification and such to be done via smart contract.
    - Something you are.
    - Something you say.

-------------------------------------------------------------------------------

- Both IOTs and Edges could be centrally owned or deployed as with some kind of service model.
- The blockchain supports monetization.
- The communication protocol and storage models can be anything:
    - Kafka.
    - MQTT.
    - Whisper.

-------------------------------------------------------------------------------

- Verifiers could be owned by the service, or standalone.
- Need to sign-up via service.
- Required to be online and respond quickly.
    - Could be some form of reward structure.
    - With penalties of course.

- Service remains alive if some verifiers fall.
- Require majority (quorum vote)
- Resistant to malicious action due to number of verifiers.
- Updated could be made one-by-one without taking the system down.

- Communicate via MQTT.
- End to end encrypted of course.
- Use nonce for freshness.

-------------------------------------------------------------------------------

- Blockchain purists might want not like this setup.
- Being a blockchain purists is unfeasible due to the multitude of unrealistic systems.

- Instead of trying to trying to hide communications
- Leverage the properties of NP-hardness combined with good design decisions.
- Avoid having one central point of failure for any component.
    - Some form of trust towards the system must exist.
- Make it as mathematically difficult as needed to 
- Assume a breach will eventually occur, and limit exposure wherever possible.



















