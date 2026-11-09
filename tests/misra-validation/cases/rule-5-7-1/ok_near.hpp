// Near misses: compliant code that resembles a violation.
#ifndef KV_RULE_5_7_1_OK_NEAR_HPP
#define KV_RULE_5_7_1_OK_NEAR_HPP

#include <cstdint>

namespace kv::rule_5_7_1::near {

/* A block comment may contain a URL such as https://example.com/path without opening a comment. */
// A line comment may contain /* the opening sequence */ without nesting anything.
inline std::uint32_t one() { return 1U; }

}  // namespace kv::rule_5_7_1::near

#endif  // KV_RULE_5_7_1_OK_NEAR_HPP
