// Near misses (near): grouped labels, default first, braced clause blocks.
#ifndef KV_RULE_9_4_2_OK_NEAR_HPP
#define KV_RULE_9_4_2_OK_NEAR_HPP

#include <cstdint>

namespace kv::rule_9_4_2::ok_near {

inline std::uint32_t weight(std::uint32_t code) {
  std::uint32_t w = code;
  switch (code) {
    default:
      w = w | 1U;
      break;
    case 1U:
    case 2U:
      w = 5U;
      break;
    case 3U: {
      const std::uint32_t t = code << 1U;
      w = t;
      break;
    }
  }
  return w;
}

inline std::uint32_t code_of(std::uint32_t k) {
  switch (k) {
    case 0U:
      return 10U;
    default:
      return 0U;
  }
}

// An explicit [[fallthrough]] terminates a branch.
inline std::uint32_t ramp(std::uint32_t code) {
  std::uint32_t w = 0U;
  switch (code) {
    case 1U:
      w = 1U;
      [[fallthrough]];
    case 2U:
      w = w + 2U;
      break;
    default:
      break;
  }
  return w;
}

// The one exception to the default label: an unscoped enumeration without a fixed underlying type, every
// enumerator listed.
enum Mode { kIdle, kRun };

inline std::uint32_t cost(Mode m) {
  std::uint32_t c = 0U;
  switch (m) {
    case kIdle:
      c = 1U;
      break;
    case kRun:
      c = 2U;
      break;
  }
  return c;
}

}  // namespace kv::rule_9_4_2::ok_near

#endif  // KV_RULE_9_4_2_OK_NEAR_HPP
