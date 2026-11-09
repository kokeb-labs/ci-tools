// Near misses: compliant code that resembles a violation.
#ifndef KV_RULE_4_1_2_IMPLICIT_COPY_OK_NEAR_HPP
#define KV_RULE_4_1_2_IMPLICIT_COPY_OK_NEAR_HPP

#include <cstdint>

namespace kv::rule_4_1_2_implicit_copy::near {

// No user-declared copy operation or destructor: the implicit copy is not deprecated (rule of zero).
struct Reading {
  std::uint32_t raw{0U};
};
inline std::uint32_t copy_raw(const Reading& r) {
  const Reading c(r);
  return c.raw;
}

}  // namespace kv::rule_4_1_2_implicit_copy::near

#endif  // KV_RULE_4_1_2_IMPLICIT_COPY_OK_NEAR_HPP
