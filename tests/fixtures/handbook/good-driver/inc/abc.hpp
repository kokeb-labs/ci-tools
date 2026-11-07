#pragma once
#include <array>
#include <cstdint>
// A comment that says new, delete, throw and virtual is fine.
namespace abc {
class Abc {
 public:
  Abc(const Abc&) = delete;
  Abc& operator=(const Abc&) = delete;
  static constexpr std::uint32_t kBig = 1'000'000;
  const char* Name() const noexcept { return "new delete throw"; }
};
}  // namespace abc
