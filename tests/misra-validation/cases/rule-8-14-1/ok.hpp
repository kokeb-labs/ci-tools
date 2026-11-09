// Compliant: the write happens in its own statement, outside the logical expression.
#ifndef KV_RULE_8_14_1_OK_HPP
#define KV_RULE_8_14_1_OK_HPP

#include <cstdint>

namespace kv::rule_8_14_1::ok {

struct Port {
  std::uint32_t reads{0U};
};

inline bool ready(Port& port, bool enabled) {
  if (enabled) {
    ++port.reads;
  }
  return enabled && (port.reads > 3U);
}

}  // namespace kv::rule_8_14_1::ok

#endif  // KV_RULE_8_14_1_OK_HPP
