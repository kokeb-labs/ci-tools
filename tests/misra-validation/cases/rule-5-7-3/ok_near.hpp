// Near misses: compliant code that resembles a violation.
#ifndef KV_RULE_5_7_3_OK_NEAR_HPP
#define KV_RULE_5_7_3_OK_NEAR_HPP

#include <cstdint>

namespace kv::rule_5_7_3::near {

// A path with a backslash in the middle of a comment: C:\temp\file.
// A comment that ends with a slash /
inline std::uint32_t three() { return 3U; }

}  // namespace kv::rule_5_7_3::near

#endif  // KV_RULE_5_7_3_OK_NEAR_HPP
