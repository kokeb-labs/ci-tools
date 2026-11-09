// Seeded violation: a handler takes a class-type exception by value.
namespace kv::rule_18_3_2::bad {

struct Fault {
  int code = 0;
};

int guard() {
  try {  // seeded: clang
    return 0;
  } catch (Fault f) {  // seeded: gcc
    return f.code;
  }
}

}  // namespace kv::rule_18_3_2::bad
