// Compliant: a scoped enum with a fixed type, compared only, never used as a number.
#ifndef KV_RULE_10_2_3_OK_HPP
#define KV_RULE_10_2_3_OK_HPP

#include <cstdint>

namespace kv::rule_10_2_3::ok {

enum class Level : std::uint8_t { kLow, kHigh };

inline bool is_high(Level l) { return l == Level::kHigh; }

}  // namespace kv::rule_10_2_3::ok

#endif  // KV_RULE_10_2_3_OK_HPP
