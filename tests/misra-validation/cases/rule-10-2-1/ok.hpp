// Compliant: the enumeration names its underlying type.
#ifndef KV_RULE_10_2_1_OK_HPP
#define KV_RULE_10_2_1_OK_HPP

#include <cstdint>

namespace kv::rule_10_2_1::ok {

enum class Mode : std::uint8_t { kIdle, kRun };

inline Mode next(Mode m) { return (m == Mode::kIdle) ? Mode::kRun : Mode::kIdle; }

}  // namespace kv::rule_10_2_1::ok

#endif  // KV_RULE_10_2_1_OK_HPP
