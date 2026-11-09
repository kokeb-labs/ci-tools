// Compliant: the choice is made outside the macro invocation.
#ifndef KV_RULE_19_3_5_OK_HPP
#define KV_RULE_19_3_5_OK_HPP

#include <cstdint>

#define KV_RULE_19_3_5_PICK(X) (X)

namespace kv::rule_19_3_5::ok {

#ifdef KV_FAST
constexpr std::uint32_t kChoice = 1U;
#else
constexpr std::uint32_t kChoice = 2U;
#endif

inline std::uint32_t pick() { return KV_RULE_19_3_5_PICK(kChoice); }

}  // namespace kv::rule_19_3_5::ok

#undef KV_RULE_19_3_5_PICK

#endif  // KV_RULE_19_3_5_OK_HPP
