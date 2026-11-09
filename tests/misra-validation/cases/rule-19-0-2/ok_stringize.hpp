// Near miss: a function-like macro that uses #, which the guideline's exception permits.
#ifndef KV_RULE_19_0_2_OK_STRINGIZE_HPP
#define KV_RULE_19_0_2_OK_STRINGIZE_HPP

#define KV_RULE_19_0_2_NAME(X) #X

namespace kv::rule_19_0_2::ok_stringize {

constexpr const char* kName = KV_RULE_19_0_2_NAME(adc);

[[nodiscard]] inline bool named() { return kName != nullptr; }

}  // namespace kv::rule_19_0_2::ok_stringize

#undef KV_RULE_19_0_2_NAME

#endif  // KV_RULE_19_0_2_OK_STRINGIZE_HPP
