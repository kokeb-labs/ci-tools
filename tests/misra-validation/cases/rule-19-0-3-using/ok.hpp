// Compliant: the using-declaration follows every #include.
#ifndef KV_RULE_19_0_3_USING_OK_HPP
#define KV_RULE_19_0_3_USING_OK_HPP

#include <cstddef>
#include <cstdint>

namespace kv::rule_19_0_3_using::ok {

using std::size_t;

constexpr size_t kCount = 2U;
constexpr std::uint8_t kValue = 1U;

}  // namespace kv::rule_19_0_3_using::ok

#endif  // KV_RULE_19_0_3_USING_OK_HPP
