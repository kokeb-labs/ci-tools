// Near misses: compliant code that resembles a violation.
#ifndef KV_RULE_5_0_1_OK_NEAR_HPP
#define KV_RULE_5_0_1_OK_NEAR_HPP


namespace kv::rule_5_0_1::near {

// Two question marks at the end, without a trigraph character after them.
inline const char* doubt() { return "Really??"; }

}  // namespace kv::rule_5_0_1::near

#endif  // KV_RULE_5_0_1_OK_NEAR_HPP
