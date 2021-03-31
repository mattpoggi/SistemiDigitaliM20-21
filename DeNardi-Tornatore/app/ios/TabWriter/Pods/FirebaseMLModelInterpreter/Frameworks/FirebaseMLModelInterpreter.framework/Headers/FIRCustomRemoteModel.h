#import <Foundation/Foundation.h>


#import <FirebaseMLCommon/FirebaseMLCommon.h>


NS_ASSUME_NONNULL_BEGIN

/** A custom model that is stored remotely on the server and downloaded to the device. */
NS_SWIFT_NAME(CustomRemoteModel)
@interface FIRCustomRemoteModel : FIRRemoteModel

/**
 * Creates a new instance with the given values.
 *
 * @param name The name of the remote model. Specify the name assigned to the model when it was
 *     uploaded to the Firebase Console.
 * @return A new `CustomRemoteModel` instance.
 */
- (instancetype)initWithName:(NSString *)name NS_DESIGNATED_INITIALIZER;

/** Unavailable. */
- (instancetype)init NS_UNAVAILABLE;

@end

NS_ASSUME_NONNULL_END
