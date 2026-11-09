// Compliant: the failure is returned to the caller; control flow stays structured.
#ifndef KV_RULE_21_10_2_OK_HPP
#define KV_RULE_21_10_2_OK_HPP

#include <cstdint>

namespace kv::rule_21_10_2::ok {

enum class Step : std::uint8_t { kDone, kRetry };

[[nodiscard]] inline Step attempt(bool ready) { return ready ? Step::kDone : Step::kRetry; }

}  // namespace kv::rule_21_10_2::ok

#endif  // KV_RULE_21_10_2_OK_HPP
