// Compliant: the stringised parameter is not pasted.
#ifndef KV_RULE_19_3_2_OK_HPP
#define KV_RULE_19_3_2_OK_HPP

#define KV_RULE_19_3_2_TEXT(P) #P

namespace kv::rule_19_3_2::ok {

constexpr const char* kName = KV_RULE_19_3_2_TEXT(adc);

}  // namespace kv::rule_19_3_2::ok

#undef KV_RULE_19_3_2_TEXT

#endif  // KV_RULE_19_3_2_OK_HPP
