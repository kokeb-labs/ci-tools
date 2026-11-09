// Near misses: compliant code that resembles a violation.
#ifndef KV_RULE_4_1_2_STRSTREAM_OK_NEAR_HPP
#define KV_RULE_4_1_2_STRSTREAM_OK_NEAR_HPP

#include <string_view>

namespace kv::rule_4_1_2_strstream::near {

// Text parsed from a string_view: the replacement for strstream reading.
inline bool starts_with_digit(std::string_view s) { return s.find_first_of("0123456789") == 0U; }

}  // namespace kv::rule_4_1_2_strstream::near

#endif  // KV_RULE_4_1_2_STRSTREAM_OK_NEAR_HPP
