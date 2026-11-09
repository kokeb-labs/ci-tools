// Compliant: events are reported through an explicit status, not through signals.
#ifndef KV_RULE_21_10_3_OK_HPP
#define KV_RULE_21_10_3_OK_HPP

#include <cstdint>

namespace kv::rule_21_10_3::ok {

enum class Event : std::uint8_t { kNone, kStop };

[[nodiscard]] inline Event poll(bool stop_requested) { return stop_requested ? Event::kStop : Event::kNone; }

}  // namespace kv::rule_21_10_3::ok

#endif  // KV_RULE_21_10_3_OK_HPP
