// Compliant: the scoped-enum switch lists every enumerator and still has a default label.
#ifndef KV_RULE_9_4_2_SCOPED_ENUM_OK_HPP
#define KV_RULE_9_4_2_SCOPED_ENUM_OK_HPP

#include <cstdint>

namespace kv::rule_9_4_2_scoped_enum::ok {

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
    default:
      break;
  }
  return c;
}

}  // namespace kv::rule_9_4_2_scoped_enum::ok

#endif  // KV_RULE_9_4_2_SCOPED_ENUM_OK_HPP
