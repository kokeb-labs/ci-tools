// Near miss: a deliberate infinite while (true) loop, permitted by the guideline's exception.
#ifndef KV_RULE_0_0_2_OK_LOOP_HPP
#define KV_RULE_0_0_2_OK_LOOP_HPP

#include <cstdint>

namespace kv::rule_0_0_2::ok_loop {

inline std::uint32_t wait_for(const volatile std::uint32_t& status) {
  while (true) {
    const std::uint32_t s = status;
    if ((s & 1U) != 0U) {
      return s;
    }
  }
}

}  // namespace kv::rule_0_0_2::ok_loop

#endif  // KV_RULE_0_0_2_OK_LOOP_HPP
