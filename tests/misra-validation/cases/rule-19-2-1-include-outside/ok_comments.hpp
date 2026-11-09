// Near miss: several comment lines before the guard.
//
// The guard below wraps the whole file.
/* A block comment is fine too. */
#ifndef KV_RULE_19_2_1_INCLUDE_OUTSIDE_OK_COMMENTS_HPP
#define KV_RULE_19_2_1_INCLUDE_OUTSIDE_OK_COMMENTS_HPP

#include <cstdint>

namespace kv::rule_19_2_1_include_outside::ok_comments {

inline std::uint8_t two() { return 2U; }

}  // namespace kv::rule_19_2_1_include_outside::ok_comments

#endif  // KV_RULE_19_2_1_INCLUDE_OUTSIDE_OK_COMMENTS_HPP
