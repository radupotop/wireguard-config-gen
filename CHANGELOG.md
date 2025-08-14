## 0.7.1

- Move codebase to a proper Python module

## 0.7.0

- Added the option to have declare a server machine as **passive**:
  - with the directive `IsPassive: true` directly under the machine name in `interfaces.yaml`
  - all the endpoints for this server's conf will be omitted
  - this becomes a passive server which relies on its clients to connect first
- Refactor

## 0.6.6

- outdir fixes

## 0.6.5

- Add support for multiple topologies: mesh and star

## 0.6.4

- Refactor
- Read outdir from yaml conf.

## 0.6.3

- Outdir fixes

## 0.6.2

- Do not hardcode output dir so that multiple subnets can be managed.
  - multiple configurations can be managed in parallel, serving different sets of clients,
living on different subnets.

## 0.6.1

- Fix parse version

## 0.6.0

- Add version to `result.yaml`

## 0.5.1

- Fix combination sorting

## 0.5.0

- First stable release
- Unique PresharedKeyPairs combinations feature by @Kaurin
- Interface DNS support by @Kaurin
