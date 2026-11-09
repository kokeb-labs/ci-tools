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

enum class Mode : std::uint8_t { kIdle, kRun };

inline std::uint32_t cost(Mode m) {
  std::uint32_t c = 0U;
  switch (m) {
    case Mode::kIdle:
      c = 1U;
      break;
    case Mode::kRun:
      c = 2U;
      break;
  }
  return c;
}

}  // namespace kv::rule_9_4_2::ok_near

#endif  // KV_RULE_9_4_2_OK_NEAR_HPP
