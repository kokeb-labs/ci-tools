// Seeded violation: an operation that may be NaN is compared.
#include <cstdint>

namespace kv::dir_0_3_1_nan::bad {

bool above(double a, double b, double limit) {
  const double q = a / b;  // NaN when both are zero
  return q > limit;  // seeded
}

}  // namespace kv::dir_0_3_1_nan::bad
