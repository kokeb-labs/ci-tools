#ifndef KV_RULE_18_5_2_OK_HPP
#define KV_RULE_18_5_2_OK_HPP

// Compliant: the fault is reported to the caller, which decides how to recover.
#include <cstdint>

namespace kv::rule_18_5_2::ok_quick_exit {

enum class Fault : std::uint8_t { kNone, kHard, kSoft };

[[nodiscard]] inline Fault fatal(bool hard) { return hard ? Fault::kHard : Fault::kSoft; }

}  // namespace kv::rule_18_5_2::ok_quick_exit

#endif  // KV_RULE_18_5_2_OK_HPP
