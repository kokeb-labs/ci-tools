// Near misses: compliant code that resembles a violation.
#ifndef KV_DIR_0_3_1_INFINITY_OK_NEAR_HPP
#define KV_DIR_0_3_1_INFINITY_OK_NEAR_HPP

#include <cmath>
#include <cstdint>

namespace kv::dir_0_3_1_infinity::near {

// A divisor that is a non-zero constant, applied to an input already checked to be finite and bounded.
inline std::int32_t quarter(double sum) {
  std::int32_t out = 0;
  if (std::isfinite(sum) && (sum < 4000.0) && (sum > -4000.0)) {
    out = static_cast<std::int32_t>(sum / 4.0);
  }
  return out;
}

}  // namespace kv::dir_0_3_1_infinity::near

#endif  // KV_DIR_0_3_1_INFINITY_OK_NEAR_HPP
