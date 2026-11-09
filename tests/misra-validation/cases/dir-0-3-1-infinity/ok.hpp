// Compliant: inputs and result are checked for NaN, infinity and range before use.
#ifndef KV_DIR_0_3_1_INFINITY_OK_HPP
#define KV_DIR_0_3_1_INFINITY_OK_HPP

#include <cmath>
#include <cstdint>

namespace kv::dir_0_3_1_infinity::ok {

inline std::int32_t ratio(double num, double den) {
  std::int32_t out = 0;
  if (std::isfinite(num) && std::isfinite(den) && (den != 0.0)) {
    const double q = num / den;
    if (std::isfinite(q) && (q < 1000.0) && (q > -1000.0)) {
      out = static_cast<std::int32_t>(q);
    }
  }
  return out;
}

}  // namespace kv::dir_0_3_1_infinity::ok

#endif  // KV_DIR_0_3_1_INFINITY_OK_HPP
