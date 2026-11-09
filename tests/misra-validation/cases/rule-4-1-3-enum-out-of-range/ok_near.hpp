// Near misses: compliant code that resembles a violation.
#ifndef KV_RULE_4_1_3_ENUM_OUT_OF_RANGE_OK_NEAR_HPP
#define KV_RULE_4_1_3_ENUM_OUT_OF_RANGE_OK_NEAR_HPP

#include <cstdint>

namespace kv::rule_4_1_3_enum_out_of_range::near {

// A fixed underlying type makes every value of that type valid, even one with no enumerator.
enum class Code : std::uint8_t { kNone = 0U, kBus = 1U };
inline Code from_byte() { return static_cast<Code>(200U); }

// A value inside the range of an enumeration without a fixed type.
enum Level { kLow, kMid, kHigh };
inline Level mid() { return static_cast<Level>(1); }

}  // namespace kv::rule_4_1_3_enum_out_of_range::near

#endif  // KV_RULE_4_1_3_ENUM_OUT_OF_RANGE_OK_NEAR_HPP
