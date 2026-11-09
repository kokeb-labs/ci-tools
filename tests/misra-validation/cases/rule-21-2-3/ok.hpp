// Compliant: the reset is a function of the program itself; no command processor is involved.
#ifndef KV_RULE_21_2_3_OK_HPP
#define KV_RULE_21_2_3_OK_HPP

#include <cstdint>

namespace kv::rule_21_2_3::ok {

enum class ResetResult : std::uint8_t { kDone, kRefused };

[[nodiscard]] inline ResetResult reset_device(bool allowed) {
  return allowed ? ResetResult::kDone : ResetResult::kRefused;
}

}  // namespace kv::rule_21_2_3::ok

#endif  // KV_RULE_21_2_3_OK_HPP
