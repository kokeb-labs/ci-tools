#ifndef KV_RULE_18_3_2_OK_HPP
#define KV_RULE_18_3_2_OK_HPP

// Compliant: errors travel as return values; the code has no throw, try or catch.
#include <cstdint>

namespace kv::rule_18_3_2::ok {

enum class Status : std::uint8_t { kOk, kTimeout };

[[nodiscard]] inline Status poll(std::uint32_t ticks) { return (ticks == 0U) ? Status::kTimeout : Status::kOk; }

}  // namespace kv::rule_18_3_2::ok

#endif  // KV_RULE_18_3_2_OK_HPP
