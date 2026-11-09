// Near miss: the parameter is not parenthesised, but no argument holds a top-level operator.
#ifndef KV_RULE_19_3_4_OK_PLAIN_HPP
#define KV_RULE_19_3_4_OK_PLAIN_HPP

#include <cstdint>

#define KV_RULE_19_3_4_BELOW(X, LIM) (X < LIM)

namespace kv::rule_19_3_4::ok_plain {

[[nodiscard]] inline bool below(std::int32_t a) { return KV_RULE_19_3_4_BELOW(a, 10); }

}  // namespace kv::rule_19_3_4::ok_plain

#undef KV_RULE_19_3_4_BELOW

#endif  // KV_RULE_19_3_4_OK_PLAIN_HPP
