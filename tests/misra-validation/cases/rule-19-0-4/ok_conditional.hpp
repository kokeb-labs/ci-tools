// Near miss: the file defines the macro under #if and undefines it again.
#ifndef KV_RULE_19_0_4_OK_CONDITIONAL_HPP
#define KV_RULE_19_0_4_OK_CONDITIONAL_HPP

#include <cstdint>

#if defined(KV_RULE_19_0_4_WIDE)
#define KV_RULE_19_0_4_WIDTH 32
#else
#define KV_RULE_19_0_4_WIDTH 16
#endif

namespace kv::rule_19_0_4::ok_conditional {

constexpr std::uint8_t kWidth = KV_RULE_19_0_4_WIDTH;

}  // namespace kv::rule_19_0_4::ok_conditional

#undef KV_RULE_19_0_4_WIDTH

#endif  // KV_RULE_19_0_4_OK_CONDITIONAL_HPP
