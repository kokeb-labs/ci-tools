// Near misses: compliant code that resembles a violation.
#ifndef KV_RULE_5_13_1_OK_NEAR_HPP
#define KV_RULE_5_13_1_OK_NEAR_HPP


namespace kv::rule_5_13_1::near {

// Standard escapes, an escaped question mark, a hex escape and a NUL.
inline const char* standard() { return "\t\?\x41\0"; }

}  // namespace kv::rule_5_13_1::near

#endif  // KV_RULE_5_13_1_OK_NEAR_HPP
