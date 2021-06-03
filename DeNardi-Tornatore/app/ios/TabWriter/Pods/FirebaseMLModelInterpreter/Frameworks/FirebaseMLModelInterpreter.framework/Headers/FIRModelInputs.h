#import <Foundation/Foundation.h>

NS_ASSUME_NONNULL_BEGIN

/** Input data for a Firebase custom model. */
NS_SWIFT_NAME(ModelInputs)
DEPRECATED_MSG_ATTRIBUTE(
    "This API is deprecated. Please see updated custom model implementation instructions at "
    "https://firebase.google.com/docs/ml/ios/use-custom-models")
@interface FIRModelInputs : NSObject

/**
 * Appends an input at the next index. The index starts from 0 and is incremented each time an
 * input is added.
 *
 * @param input Input data for the next index. Input can be `NSData`, or a one-dimensional or
 *     multi-dimensional array of `NSNumber`s (float, int, char, long).
 * @param error The error, if any, during the operation, including
 *     `MLKitErrorDomainCode.InvalidArgument` when:
 *     - `input` is nil.
 *     - The input type is neither `NSData` nor `NSArray`.
 * @return Whether the operation is successful.
 */
- (BOOL)addInput:(id)input error:(NSError **)error;

@end

NS_ASSUME_NONNULL_END

