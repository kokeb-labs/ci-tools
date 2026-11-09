// Near misses: compliant code that resembles a violation.
#ifndef KV_RULE_5_13_2_OK_NEAR_HPP
#define KV_RULE_5_13_2_OK_NEAR_HPP


namespace kv::rule_5_13_2::near {

// Each numeric escape ends at another escape or at the end of the literal.
inline const char* two() { return "\x41\x42"; }
inline const char* last() { return "AB\101"; }
inline char single() { return '\x7F'; }

}  // namespace kv::rule_5_13_2::near

#endif  // KV_RULE_5_13_2_OK_NEAR_HPP
