# 2020-06-02 -- v0.20.0
- Updated the TensorFlow Lite dependency from `TensorFlowLite` 1.14.0 to
  `TensorFlowLiteObjC` 2.1.0.

# 2019-10-08 -- v0.19.0
- Adds `CustomRemoteModel` and `CustomLocalModel` as instantiable subclasses of
  `RemoteModel` and `LocalModel` classes, respectively.
- **Breaking change:** Updates the initializers for `ModelInterpreter` and
  removes the `ModelOptions` class. The `ModelInterpreter` can be initialized
  with either a `CustomRemoteModel` or `CustomLocalModel`, but not both.
- **Breaking change:** Implicit model downloading is no longer available through
  the `ModelInterpreter`. You must invoke the `ModelManager`'s
  `download(_:conditions:)` API to download `CustomRemoteModel`s. Please see the
  Model Interpreter QuickStart app for an example of how to download
  `CustomRemoteModel`s.

# 2019-09-03 -- v0.18.0
- Updated the TensorFlow Lite dependency from `TensorFlowLite` 1.13.1 to
  `TensorFlowLiteObjC` 1.14.0.

# 2019-07-09 -- v0.17.0
- Bug fixes.

# 2019-05-07 -- v0.16.0
- Upgraded TensorFlowLite dependency from 1.12.0 to 1.13.1.

# 2019-03-19 -- v0.15.0
- Bug fixes.

# 2019-01-22 -- v0.14.0
- Defining and registering `CloudModelSource` and `LocalModelSource` custom models has
  been moved to `FirebaseMLCommon`. Import the `FirebaseMLCommon` module in your
  Swift or Objective-C files to use the new API.
- Upgraded TensorFlowLite dependency from 1.10.1 to 1.12.0.

# 2018-11-20 -- v0.13.0
- Bug fixes.

# 2018-10-09 -- v0.12.0
- Upgraded TensorFlowLite dependency from 0.1.7 to 1.10.1.

# 2018-07-31 -- v0.11.0
- Bug fixes.
