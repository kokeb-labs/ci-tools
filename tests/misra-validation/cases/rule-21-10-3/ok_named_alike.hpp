// Compliant near miss: our own Signal type and a raise_alarm function; nothing from <csignal>.
#ifndef KV_RULE_21_10_3_OK_NAMED_ALIKE_HPP
#define KV_RULE_21_10_3_OK_NAMED_ALIKE_HPP

#include <cstdint>

namespace kv::rule_21_10_3::ok_named_alike {

enum class Signal : std::uint8_t { kNone, kAlarm };

[[nodiscard]] inline Signal raise_alarm(bool over_limit) { return over_limit ? Signal::kAlarm : Signal::kNone; }

}  // namespace kv::rule_21_10_3::ok_named_alike

#endif  // KV_RULE_21_10_3_OK_NAMED_ALIKE_HPP
