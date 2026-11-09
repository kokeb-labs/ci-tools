// Near misses: compliant code that resembles a violation.
#ifndef KV_DIR_0_3_1_NAN_OK_NEAR_HPP
#define KV_DIR_0_3_1_NAN_OK_NEAR_HPP

#include <cmath>

namespace kv::dir_0_3_1_nan::near {

// The quotient is compared only once it is known not to be NaN.
inline bool above(double a, double b, double limit) {
  bool out = false;
  if (std::isfinite(a) && std::isfinite(b) && (b != 0.0)) {
    const double q = a / b;
    out = (!std::isnan(q)) && (q > limit);
  }
  return out;
}

}  // namespace kv::dir_0_3_1_nan::near

#endif  // KV_DIR_0_3_1_NAN_OK_NEAR_HPP
