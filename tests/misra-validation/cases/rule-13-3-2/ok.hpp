// Compliant: no default arguments on virtual functions; a non-virtual wrapper supplies the default.
#ifndef KV_RULE_13_3_2_OK_HPP
#define KV_RULE_13_3_2_OK_HPP

#include <cstdint>

namespace kv::rule_13_3_2::ok {

class Filter {
 public:
  Filter() = default;
  Filter(const Filter&) = delete;
  Filter(Filter&&) = delete;
  Filter& operator=(const Filter&) = delete;
  Filter& operator=(Filter&&) = delete;
  virtual ~Filter() = default;
  virtual std::uint32_t apply(std::uint32_t gain) const = 0;
  std::uint32_t apply_default() const { return apply(1U); }
};

class Strong final : public Filter {
 public:
  Strong() = default;
  Strong(const Strong&) = delete;
  Strong(Strong&&) = delete;
  Strong& operator=(const Strong&) = delete;
  Strong& operator=(Strong&&) = delete;
  ~Strong() override = default;
  std::uint32_t apply(std::uint32_t gain) const override { return gain; }
};

inline std::uint32_t run(const Filter& f) { return f.apply_default(); }

}  // namespace kv::rule_13_3_2::ok

#endif  // KV_RULE_13_3_2_OK_HPP
