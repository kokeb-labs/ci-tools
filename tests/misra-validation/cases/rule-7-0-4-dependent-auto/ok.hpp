// Compliant: both operands of & are std::uint32_t. `s` is an auto variable in an out-of-line member of a
// constrained class template, initialised from a member function that returns Result<std::uint32_t>.
#ifndef KV_RULE_7_0_4_DEPENDENT_AUTO_OK_HPP
#define KV_RULE_7_0_4_DEPENDENT_AUTO_OK_HPP

#include <concepts>
#include <cstdint>

namespace kv::rule_7_0_4_dependent_auto::ok {

template <typename T>
struct Result {
  T value;
};

template <typename P>
concept Port = requires(P& p) {
  { p.Read() } -> std::same_as<std::uint32_t>;
};

template <Port P>
class Driver {
 public:
  explicit Driver(P& port) : port_(port) {}
  bool Active();

 private:
  static constexpr std::uint32_t kActive = 1U;
  Result<std::uint32_t> read32();
  P& port_;
};

template <Port P>
Result<std::uint32_t> Driver<P>::read32() {
  return Result<std::uint32_t>{port_.Read()};
}

template <Port P>
bool Driver<P>::Active() {
  const auto s = read32();
  return (s.value & kActive) != 0U;
}

class FakePort {
 public:
  std::uint32_t Read() { return level_; }

 private:
  std::uint32_t level_ = 1U;
};

inline bool Probe(FakePort& port) {
  Driver<FakePort> driver{port};
  return driver.Active();
}

}  // namespace kv::rule_7_0_4_dependent_auto::ok

#endif  // KV_RULE_7_0_4_DEPENDENT_AUTO_OK_HPP
