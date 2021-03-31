# 2020-06-02 -- v0.20.0
- Adds `getLatestModelFilePath(_:completion:)` API to `ModelManager` class for
  getting the absolute file path on the device for a downloaded custom remote
  model.

# 2019-10-08 -- v0.19.0
- **Breaking change:** Updates `ModelManager` with the following API changes:
  - Added `modelManager(app:)` for a custom Firebase app. Note that download
    management for custom Firebase apps is currently only supported for the
    Translate SDK.
  - Removed the `RemoteModel` and `LocalModel` registration APIs. You no
    longer need to register models before using them.
  - Added a model download conditions parameter in the
    `download(_:conditions)` API to make it easier to tie the conditions to
    specific download requests. You can fully control when to download a model
    for the first time and when to check for model updates via this API.
  - Updated `isRemoteModelDownloaded(_:)` to `isModelDownloaded(_:)`.
  - Added `deleteDownloadedModel(_:completion:)` to delete downloaded models to
    provide you with more flexibility for managing disk space on your user's
    devices.
- **Breaking change:** `RemoteModel` and `LocalModel` initializers have been
  disabled. New subclasses have been added for AutoML, Custom, and Translate
  SDKs. Use the intializers for those subclasses to create instances of remote
  and local models. `initialConditions` and `updateConditions` are no longer
  needed for initializing a remote model. Download condition should be specified
  each time calling `download(_:conditions:)` of the `ModelManager`.

# 2019-09-03 -- v0.18.0
- Bug fixes.
- [INTERNAL] Changed the minimum iOS version from 9.0 to 8.0.

# 2019-07-09 -- v0.17.0
- Bug fixes.

# 2019-05-07 -- v0.16.0
- Adds `download(_:)` API to `ModelManager` class for downloading a remote
  model. Caller can monitor the returned `NSProgress` and receive notifications
  defined in `FIRModelDownloadNotifications.h`.

# 2019-03-19 -- v0.15.0
-  **Breaking change:** Renamed model downloading APIs in FirebaseMLCommon
  (no change to functionality):
    - Renamed `CloudModelSource` to `RemoteModel` and `LocalModelSource`
      to `LocalModel`.
    - Updated `ModelManager` methods to reflect the renaming of the model
      classes.
    - Renamed the following properties in `ModelDownloadConditions`:
      `isWiFiRequired` is now `allowsCellularAccess` and
      `canDownloadInBackground` is now `allowsBackgroundDownloading`.

# 2019-01-22 -- v0.14.0
- Adds the `ModelManager` class for downloading and managing custom models from
  the cloud.
- Adds `CloudModelSource` and `LocalModelSource` classes for defining and registering
  custom cloud and local models. These classes were previously defined in
  `FirebaseMLModelInterpreter`.
