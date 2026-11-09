// Compliant by the guideline's exception: assert(false && "string literal") marks a path not expected to run.
#ifndef KV_RULE_22_3_1_OK_EXCEPTION_HPP
#define KV_RULE_22_3_1_OK_EXCEPTION_HPP

#include <cassert>
#include <cstdint>

namespace kv::rule_22_3_1::ok_exception {

[[nodiscard]] inline std::uint8_t decode(std::uint8_t code) {
  std::uint8_t out = 0U;
  if (code < 4U) {
    out = static_cast<std::uint8_t>(code + 1U);
  } else {
    assert(false && "code out of range");
  }
  return out;
}

}  // namespace kv::rule_22_3_1::ok_exception

#endif  // KV_RULE_22_3_1_OK_EXCEPTION_HPP
